import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base

# Use SQLite in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop tables
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def override_get_db(db_session):
    def _override_get_db():
        yield db_session

    return _override_get_db


# Mock settings for Chroma DB to use a temporary directory
@pytest.fixture(autouse=True)
def mock_settings(monkeypatch, tmp_path):
    monkeypatch.setenv("POSTGRES_DB", "test_db")
    monkeypatch.setenv("CHROMA_DB_DIR", str(tmp_path / "chroma"))
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "data"))
