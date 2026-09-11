from unittest.mock import patch

from brain.model_client import KEEP_ALIVE, MODEL_NAME, call_model, warm_up


def _fake_response(content: str) -> dict:
    return {"message": {"content": content}}


@patch("brain.model_client.ollama.chat")
def test_call_model_passes_model_format_and_keep_alive(mock_chat):
    mock_chat.return_value = _fake_response('{"intent": "Unknown", "slots": {}}')

    result = call_model("open camera", now_iso="2026-01-01T00:00:00+00:00")

    assert result == '{"intent": "Unknown", "slots": {}}'
    _, kwargs = mock_chat.call_args
    assert kwargs["model"] == MODEL_NAME
    assert kwargs["format"] == "json"
    assert kwargs["options"] == {"temperature": 0}
    # Regression guard: this is what keeps the model resident between
    # requests so only server-startup warm_up() pays the disk-load cost.
    assert kwargs["keep_alive"] == KEEP_ALIVE


@patch("brain.model_client.ollama.chat")
def test_call_model_includes_command_and_time_in_user_message(mock_chat):
    mock_chat.return_value = _fake_response("{}")

    call_model("close spotify", now_iso="2026-09-11T10:00:00+00:00")

    _, kwargs = mock_chat.call_args
    messages = kwargs["messages"]
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert "close spotify" in messages[1]["content"]
    assert "2026-09-11T10:00:00+00:00" in messages[1]["content"]


@patch("brain.model_client.call_model")
def test_warm_up_makes_one_trivial_call(mock_call_model):
    mock_call_model.return_value = '{"intent": "OpenApp", "slots": {"app_name": "camera"}}'

    warm_up()

    mock_call_model.assert_called_once()
    args, kwargs = mock_call_model.call_args
    assert args[0]  # a non-empty prompt was used
    assert "now_iso" in kwargs
