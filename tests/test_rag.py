from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from src.api.server import app
from src.api.rag_chain import query_assistant


def test_query_assistant_offline_when_no_api_key(monkeypatch):
    monkeypatch.setattr("src.api.rag_chain.settings.groq_api_key", "")
    ans, docs = query_assistant("How do I fix a flat tire?")
    assert "currently offline" in ans.lower()
    assert docs == []


def test_api_chat_endpoint_success():
    client = TestClient(app)
    mock_doc = MagicMock()
    mock_doc.page_content = "Sample manual excerpt"

    with patch(
        "src.api.server.query_assistant",
        return_value=("Check tire pressure", [mock_doc]),
    ):
        response = client.post("/api/chat", json={"message": "How to pump tire?"})
        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "Check tire pressure"
        assert data["sources"] == ["Sample manual excerpt"]
