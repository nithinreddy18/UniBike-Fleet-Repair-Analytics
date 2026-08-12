def test_rag_assistant_mock(monkeypatch):
    from src.ui.tabs.assistant import respond

    def mock_query_assistant(q):
        return "This is a mocked RAG response about " + q, []

    monkeypatch.setattr("src.ui.tabs.assistant.query_assistant", mock_query_assistant)

    _, history = respond("derailleur", [])

    assert len(history) == 1
    assert history[0][0] == "derailleur"
    assert "mocked RAG response about derailleur" in history[0][1]
