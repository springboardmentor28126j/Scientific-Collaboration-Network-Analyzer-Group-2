from pydantic import BaseModel, Field, field_validator


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

    @field_validator("role")
    @classmethod
    def _role_must_be_user_or_assistant(cls, v):
        if v not in ("user", "assistant"):
            raise ValueError("role must be 'user' or 'assistant'")
        return v

    @field_validator("content")
    @classmethod
    def _content_length(cls, v):
        if not v or not v.strip():
            raise ValueError("content must not be empty")
        if len(v) > 4000:
            raise ValueError("content is too long (max 4000 characters)")
        return v


class ChatRequest(BaseModel):
    # The client sends the whole conversation so far (its own last user
    # message included); the server trims it to the configured history
    # window before calling the model. Capped here too so an oversized
    # payload is rejected outright rather than silently truncated.
    messages: list[ChatMessage] = Field(..., min_length=1, max_length=60)


class ChatResponse(BaseModel):
    reply: str
