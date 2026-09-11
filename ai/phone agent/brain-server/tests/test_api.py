from unittest.mock import patch

from fastapi.testclient import TestClient

from brain.main import app

client = TestClient(app)


def _post(text: str, model_reply: str):
    with patch("brain.main.call_model", return_value=model_reply):
        return client.post("/parse-intent", json={"text": text})


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_open_app_end_to_end():
    resp = _post(
        "open spotify",
        '{"intent": "OpenApp", "slots": {"app_name": "spotify"}}',
    )
    assert resp.status_code == 200
    assert resp.json() == {"intent": "OpenApp", "slots": {"app_name": "spotify"}}


def test_gibberish_model_output_becomes_unknown():
    resp = _post("asdkfjaslkdfj", "I'm not sure what you mean")
    assert resp.status_code == 200
    assert resp.json() == {"intent": "Unknown", "slots": {}}


def test_call_end_to_end():
    resp = _post(
        "call mom",
        '{"intent": "Call", "slots": {"contact_name": "mom"}}',
    )
    assert resp.json() == {"intent": "Call", "slots": {"contact_name": "mom", "phone_number": None}}


def test_create_reminder_end_to_end():
    resp = _post(
        "remind me to take out the trash at 6pm",
        '{"intent": "CreateReminder", "slots": {"title": "take out the trash", "time": "2026-09-10T18:00:00"}}',
    )
    body = resp.json()
    assert body["intent"] == "CreateReminder"
    assert body["slots"]["title"] == "take out the trash"
