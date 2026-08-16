"""
Shared fixtures for the domain-logic test suite (publications, collaborations,
citations, reviews).

Design decisions, spelled out because they diverge from the existing tests
in this folder:

1. Isolated database per test. The pre-existing tests (test_google_auth.py
   etc.) call TestClient(app) directly, which means they hit whatever real
   database is configured in .env -- no rollback, no cleanup, and the
   suite isn't safely re-runnable. These new tests instead override
   get_db() with a fresh in-memory SQLite database, created and dropped
   per test function. Nothing here ever touches your real Postgres/Supabase
   database, and running the suite twice in a row gives identical results.

2. Auth is bypassed via dependency override, not real JWTs. get_current_user
   normally requires a valid signed JWT *and* a live Redis session entry
   (see app/core/redis_client.py). That coupling is exactly right for
   production, but it means testing business logic (who can edit a
   publication, whether a citation's self-reference check fires, etc.)
   would otherwise require standing up Redis and minting real tokens for
   every test -- infrastructure concerns that have nothing to do with the
   domain rule under test. So these tests override get_current_user
   directly with whatever User object represents "who's making this
   request" and never touch the JWT/Redis code path at all. Auth/session
   behavior itself is what test_google_auth.py and test_redis_fallback.py
   already cover -- this suite assumes that layer works and tests what's
   on the other side of it.

3. SQLite, not Postgres, for speed and zero external dependencies -- every
   model in this codebase uses portable column types (no JSONB/ARRAY), and
   foreign keys are enforced by turning on PRAGMA foreign_keys, so
   ondelete=CASCADE/SET NULL and CheckConstraints behave the same as they
   will in production.
"""
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.dependencies import get_current_user

# app.main -> app.api.v1.router -> every endpoint module -> every model
# module it needs, so by the time `app` above is imported, every model
# class is already registered on Base.metadata. (Careful: don't add a
# separate `import app.models` here -- `import package.submodule` rebinds
# the bare name `package` in this module's namespace, which would silently
# clobber the `app` name we just bound to the FastAPI instance above.)

from app.models.user import User, UserRole, AffiliationStatus, AuthProvider
from app.models.researcher import ResearcherProfile
from app.models.institution import Institution
from app.models.publication import Publication, PublicationType, PublicationStatus


# --- Database isolation -------------------------------------------------

@pytest.fixture()
def db_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _enable_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def db_session(db_engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture()
def login_as():
    """login_as(user) makes `client` act as that user for every request
    that follows, until called again with someone else. Callable more than
    once per test -- e.g. act as the author, then switch to act as a
    different researcher to assert they get a 403."""
    def _login_as(user: User):
        app.dependency_overrides[get_current_user] = lambda: user
    yield _login_as


@pytest.fixture(autouse=True)
def _block_real_smtp(request):
    """
    Every test gets this automatically -- no test should ever depend on
    real network access, and several endpoints (accepting a collaboration
    request, inviting a project member, removing a member) trigger notify(),
    which now sends real email for a handful of notif_types. Without this,
    those tests would attempt a genuine SMTP connection on every run: slow
    at best, and a hang at worst if the mail server is unreachable (which is
    exactly what happened before this fixture existed -- see the timeout
    added to email_sender.send_email for the production-side half of this
    fix). Patched at the lowest boundary (send_email itself) so tests that
    specifically want to assert on email content can still patch a
    higher-level function like send_notification_email without conflict.

    Exemption: test_email_sender.py tests send_email itself -- its unconfigured
    SMTP warning, its logging output, its EMAIL_VERIFICATION_ENABLED skip path.
    Patching send_email out from under those tests would mean they never see
    the real function's behavior at all. That file monkeypatches smtplib.SMTP
    directly instead, so it never risks a real network call.
    """
    if request.node.fspath.basename == "test_email_sender.py":
        yield
        return
    from unittest.mock import patch
    with patch("app.core.email_sender.send_email"):
        yield


# --- Data factories -------------------------------------------------------
# Plain functions, not fixtures, so a test can create exactly as many
# users/researchers/publications as its scenario needs instead of being
# handed one fixed set.

@pytest.fixture()
def make_institution(db_session):
    def _make(name="Test University", **kwargs):
        inst = Institution(name=name, **kwargs)
        db_session.add(inst)
        db_session.commit()
        db_session.refresh(inst)
        return inst
    return _make


@pytest.fixture()
def make_user(db_session):
    counter = {"n": 0}

    def _make(
        role=UserRole.RESEARCHER, institution_id=None,
        affiliation_status=AffiliationStatus.NOT_APPLICABLE, is_active=True, email=None,
    ):
        counter["n"] += 1
        user = User(
            email=email or f"user{counter['n']}@example.com",
            password_hash="not-a-real-hash",
            role=role,
            institution_id=institution_id,
            is_active=is_active,
            is_email_verified=True,
            affiliation_status=affiliation_status,
            auth_provider=AuthProvider.LOCAL,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user
    return _make


@pytest.fixture()
def make_researcher(db_session, make_user):
    counter = {"n": 0}

    def _make(user=None, first_name=None, last_name="Researcher", **user_kwargs):
        counter["n"] += 1
        if user is None:
            user = make_user(**user_kwargs)
        profile = ResearcherProfile(
            user_id=user.user_id,
            first_name=first_name or f"First{counter['n']}",
            last_name=last_name,
        )
        db_session.add(profile)
        db_session.commit()
        db_session.refresh(profile)
        return profile
    return _make


@pytest.fixture()
def make_publication(db_session):
    def _make(
        primary_author: ResearcherProfile, title="A Test Paper",
        publication_type=PublicationType.JOURNAL_PAPER, status=PublicationStatus.DRAFT,
        institution_id=None, doi=None, publication_date=None, venue_name=None,
    ):
        pub = Publication(
            title=title, publication_type=publication_type, status=status,
            primary_author_id=primary_author.researcher_id, institution_id=institution_id,
            doi=doi, publication_date=publication_date, venue_name=venue_name,
        )
        db_session.add(pub)
        db_session.commit()
        db_session.refresh(pub)
        return pub
    return _make