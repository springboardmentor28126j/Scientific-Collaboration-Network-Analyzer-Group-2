"""
Tests for the AI chatbot. The Anthropic API itself is always mocked --
these tests check: role-based tool availability, that tool handlers pull
the right scoped data, the tool-use loop plumbing, and the endpoint's
config/error handling. They do not make real network calls.
"""
from unittest.mock import MagicMock, patch

import pytest

from app.core.config import settings
from app.models.user import UserRole
from app.services import chatbot_service


def _text_block(text):
    block = MagicMock()
    block.type = "text"
    block.text = text
    return block


def _tool_use_block(tool_id, name, tool_input):
    block = MagicMock()
    block.type = "tool_use"
    block.id = tool_id
    block.name = name
    block.input = tool_input
    return block


def _response(stop_reason, content):
    resp = MagicMock()
    resp.stop_reason = stop_reason
    resp.content = content
    return resp


class TestToolAvailability:
    def test_researcher_gets_personal_tools_only(self):
        tools = {t["name"] for t in chatbot_service._tools_for_role(UserRole.RESEARCHER)}
        assert tools == {
            "get_my_profile_and_activity", "get_my_publications", "get_my_projects", "get_my_collaborations",
        }

    def test_reviewer_gets_reviews_tool_too(self):
        tools = {t["name"] for t in chatbot_service._tools_for_role(UserRole.REVIEWER)}
        assert "get_my_reviews" in tools
        assert "get_my_publications" in tools

    def test_institution_admin_gets_institution_tool_only(self):
        tools = {t["name"] for t in chatbot_service._tools_for_role(UserRole.INSTITUTION_ADMIN)}
        assert tools == {"get_institution_overview"}

    def test_system_admin_gets_admin_tools(self):
        tools = {t["name"] for t in chatbot_service._tools_for_role(UserRole.SYSTEM_ADMIN)}
        assert tools == {"get_my_reviews", "lookup_institution", "get_system_overview"}


class TestToolExecutionScope:
    def test_researcher_tool_denied_for_wrong_role(self, db_session, make_user):
        admin = make_user(role=UserRole.SYSTEM_ADMIN)
        result = chatbot_service._execute_tool(db_session, admin, "get_my_publications", {})
        assert "error" in result

    def test_get_my_publications_returns_own_data_only(self, db_session, make_researcher, make_publication):
        me = make_researcher(first_name="Ada")
        make_publication(me, title="My Paper", status="published")
        other = make_researcher(first_name="Bob")
        make_publication(other, title="Not Mine", status="published")

        result = chatbot_service._execute_tool(db_session, me.user, "get_my_publications", {})
        assert result["total"] == 1

    def test_get_my_publications_no_profile(self, db_session, make_user):
        admin = make_user(role=UserRole.SYSTEM_ADMIN)
        result = chatbot_service._execute_tool(db_session, admin, "get_my_publications", {})
        assert "error" in result  # system_admin isn't in the allowed roles for this tool at all

    def test_get_my_reviews_system_admin_gets_all_scope(self, db_session, make_user):
        admin = make_user(role=UserRole.SYSTEM_ADMIN)
        result = chatbot_service._execute_tool(db_session, admin, "get_my_reviews", {})
        assert result["scope"] == "all"

    def test_get_my_reviews_reviewer_gets_mine_scope(self, db_session, make_user):
        reviewer = make_user(role=UserRole.REVIEWER)
        result = chatbot_service._execute_tool(db_session, reviewer, "get_my_reviews", {})
        assert result["scope"] == "mine"

    def test_lookup_institution_only_for_system_admin(self, db_session, make_user):
        institution_admin = make_user(role=UserRole.INSTITUTION_ADMIN)
        result = chatbot_service._execute_tool(db_session, institution_admin, "lookup_institution", {"institution_name": "MIT"})
        assert "error" in result

    def test_get_institution_overview_unlinked_account(self, db_session, make_user):
        admin = make_user(role=UserRole.INSTITUTION_ADMIN)
        assert admin.institution_id is None
        result = chatbot_service._execute_tool(db_session, admin, "get_institution_overview", {})
        assert "message" in result
        assert "not linked" in result["message"]


class TestRunChat:
    def test_raises_when_api_key_missing(self, db_session, make_user):
        researcher = make_user(role=UserRole.RESEARCHER)
        with patch.object(settings, "ANTHROPIC_API_KEY", ""):
            with pytest.raises(chatbot_service.ChatbotUnavailable):
                chatbot_service.run_chat(db_session, researcher, [{"role": "user", "content": "hi"}])

    def test_faq_style_question_returns_text_without_tool_call(self, db_session, make_user):
        researcher = make_user(role=UserRole.RESEARCHER)
        fake_client = MagicMock()
        fake_client.messages.create.return_value = _response(
            "end_turn", [_text_block("Go to /publications/new to submit a publication.")]
        )
        with (
            patch.object(settings, "ANTHROPIC_API_KEY", "fake-key"),
            patch.object(chatbot_service, "_get_client", return_value=fake_client),
        ):
            reply = chatbot_service.run_chat(db_session, researcher, [{"role": "user", "content": "how do I submit a publication?"}])
        assert "/publications/new" in reply
        assert fake_client.messages.create.call_count == 1

    def test_tool_use_loop_executes_tool_and_returns_final_text(self, db_session, make_researcher, make_publication):
        me = make_researcher(first_name="Ada")
        make_publication(me, title="Paper A", status="published")

        fake_client = MagicMock()
        first_response = _response(
            "tool_use", [_tool_use_block("call_1", "get_my_publications", {})]
        )
        second_response = _response("end_turn", [_text_block("You have 1 publication.")])
        fake_client.messages.create.side_effect = [first_response, second_response]

        with (
            patch.object(settings, "ANTHROPIC_API_KEY", "fake-key"),
            patch.object(chatbot_service, "_get_client", return_value=fake_client),
        ):
            reply = chatbot_service.run_chat(db_session, me.user, [{"role": "user", "content": "how many publications do I have?"}])

        assert reply == "You have 1 publication."
        assert fake_client.messages.create.call_count == 2
        # second call's messages must include the tool_result
        second_call_messages = fake_client.messages.create.call_args_list[1].kwargs["messages"]
        assert any(m["role"] == "user" and isinstance(m["content"], list) for m in second_call_messages)

    def test_api_error_raises_chatbot_unavailable(self, db_session, make_user):
        import anthropic
        researcher = make_user(role=UserRole.RESEARCHER)
        fake_client = MagicMock()
        fake_request = MagicMock()
        fake_client.messages.create.side_effect = anthropic.APIConnectionError(request=fake_request)
        with (
            patch.object(settings, "ANTHROPIC_API_KEY", "fake-key"),
            patch.object(chatbot_service, "_get_client", return_value=fake_client),
        ):
            with pytest.raises(chatbot_service.ChatbotUnavailable):
                chatbot_service.run_chat(db_session, researcher, [{"role": "user", "content": "hi"}])

    def test_gives_up_gracefully_after_max_tool_iterations(self, db_session, make_researcher, make_publication):
        me = make_researcher(first_name="Ada")
        make_publication(me, title="Paper A", status="published")
        fake_client = MagicMock()
        # Always returns tool_use, never end_turn -- simulates a model that
        # keeps calling tools without ever answering.
        fake_client.messages.create.return_value = _response(
            "tool_use", [_tool_use_block("call_x", "get_my_publications", {})]
        )
        with (
            patch.object(settings, "ANTHROPIC_API_KEY", "fake-key"),
            patch.object(chatbot_service, "_get_client", return_value=fake_client),
            patch.object(settings, "CHATBOT_MAX_TOOL_ITERATIONS", 2),
        ):
            reply = chatbot_service.run_chat(db_session, me.user, [{"role": "user", "content": "?"}])
        assert "couldn't pull together" in reply
        assert fake_client.messages.create.call_count == 2


class TestChatEndpoint:
    def test_message_too_long_rejected(self, client, login_as, make_user):
        researcher = make_user(role=UserRole.RESEARCHER)
        login_as(researcher)
        resp = client.post("/api/v1/chatbot/message", json={"messages": [{"role": "user", "content": "x" * 5000}]})
        assert resp.status_code == 422

    def test_requires_auth(self, client):
        resp = client.post("/api/v1/chatbot/message", json={"messages": [{"role": "user", "content": "hi"}]})
        assert resp.status_code == 401

    def test_returns_503_when_not_configured(self, client, login_as, make_user):
        researcher = make_user(role=UserRole.RESEARCHER)
        login_as(researcher)
        with patch.object(settings, "ANTHROPIC_API_KEY", ""):
            resp = client.post("/api/v1/chatbot/message", json={"messages": [{"role": "user", "content": "hi"}]})
        assert resp.status_code == 503

    def test_happy_path_returns_reply(self, client, login_as, make_user):
        researcher = make_user(role=UserRole.RESEARCHER)
        login_as(researcher)
        fake_client = MagicMock()
        fake_client.messages.create.return_value = _response("end_turn", [_text_block("Sure, here's how...")])
        with (
            patch.object(settings, "ANTHROPIC_API_KEY", "fake-key"),
            patch.object(chatbot_service, "_get_client", return_value=fake_client),
        ):
            resp = client.post("/api/v1/chatbot/message", json={"messages": [{"role": "user", "content": "how do I submit a publication?"}]})
        assert resp.status_code == 200, resp.text
        assert resp.json()["reply"] == "Sure, here's how..."
