"""API integration tests."""
import pytest
from fastapi.testclient import TestClient

from src.doc_analysis.main import app
from src.doc_analysis.db.session import SessionLocal, engine
from src.doc_analysis.db.models import Base


@pytest.fixture
def db():
    """Database fixture."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert data["service"] == "Document Analysis Service"


def test_parse_document_invalid_file(client):
    """Test parsing with invalid file type."""
    response = client.post(
        "/api/v1/documents/parse",
        files={"file": ("test.txt", b"some content", "text/plain")},
    )
    assert response.status_code == 400


def test_get_nonexistent_document(client):
    """Test getting a document that doesn't exist."""
    response = client.get("/api/v1/documents/999")
    assert response.status_code == 404


def test_get_nonexistent_section(client):
    """Test getting a section that doesn't exist."""
    response = client.get("/api/v1/documents/1/sections/1.1")
    assert response.status_code == 404
