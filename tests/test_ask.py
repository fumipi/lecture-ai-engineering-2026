from types import SimpleNamespace

from app import ask


def test_main_reuses_chat_for_follow_up_questions(monkeypatch):
    questions = []

    class FakeChat:
        def send_message(self, question):
            questions.append(question)
            return SimpleNamespace(text=f"answer: {question}", usage_metadata=None)

    chat = FakeChat()
    client = SimpleNamespace(chats=SimpleNamespace(create=lambda model: chat))
    monkeypatch.setattr(ask.genai, "Client", lambda api_key: client)
    monkeypatch.setattr(ask, "get_api_key", lambda: "test-key")
    monkeypatch.setattr("sys.argv", ["app.ask", "最初の質問"])
    inputs = iter(["続けて質問", "exit"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))

    ask.main()

    assert questions == ["最初の質問", "続けて質問"]