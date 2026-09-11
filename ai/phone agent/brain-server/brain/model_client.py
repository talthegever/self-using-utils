"""Talks to the local Ollama model. This module's only job is text -> raw
text. It never executes anything and never sees a validated intent -
validation happens in schema.py after this returns."""

import ollama

MODEL_NAME = "qwen2.5:3b-instruct"

SYSTEM_PROMPT = """You turn a spoken command into exactly one JSON object and nothing else.

You must output ONLY the JSON object - no prose, no explanation, no markdown fences.

The JSON object must be exactly one of these shapes:

{"intent": "OpenApp", "slots": {"app_name": "<app name as heard>"}}
{"intent": "CloseApp", "slots": {"app_name": "<app name as heard>"}}
{"intent": "Call", "slots": {"contact_name": "<name as heard>"}}
{"intent": "Call", "slots": {"phone_number": "<digits as heard>"}}
{"intent": "CreateCalendarEvent", "slots": {"title": "<title>", "start_time": "<ISO 8601 datetime>", "end_time": "<ISO 8601 datetime or omit>"}}
{"intent": "CreateReminder", "slots": {"title": "<title>", "time": "<ISO 8601 datetime>"}}
{"intent": "Unknown", "slots": {}}

Rules:
- If the command is ambiguous, not one of the above actions, or missing
  required information, output the Unknown shape. Never guess.
- For Call, include exactly one of contact_name or phone_number, never both.
- Resolve relative dates/times (e.g. "tomorrow at 3pm") against the current
  time you are given in the user message, and always output absolute ISO
  8601 datetimes.
"""


# Keep the model resident in Ollama between requests so only the very first
# call after server startup (handled by warm_up()) pays the disk-load cost.
KEEP_ALIVE = "30m"


def call_model(text: str, now_iso: str) -> str:
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Current time: {now_iso}\nCommand: {text}"},
        ],
        format="json",
        options={"temperature": 0},
        keep_alive=KEEP_ALIVE,
    )
    return response["message"]["content"]


def warm_up() -> None:
    """Force Ollama to load MODEL_NAME into memory now, at server startup,
    instead of on the user's first real command (a cold load can take well
    over a minute and blows past the phone's request timeout)."""
    call_model("open camera", now_iso="2026-01-01T00:00:00+00:00")
