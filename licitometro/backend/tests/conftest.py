import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from backend.main import app
from backend.config import settings
from backend.database import Base, get_db

# Create test database
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/licitometro_test"

@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(engine):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user():
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword",
        "full_name": "Test User"
    }

@pytest.fixture
def test_user_token(client, test_user):
    response = client.post(
        f"{settings.api_v1_prefix}/auth/token",
        data={
            "username": test_user["username"],
            "password": test_user["password"]
        }
    )
    return response.json()["access_token"]
