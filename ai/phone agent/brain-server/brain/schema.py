"""The fixed intent schema described in design.txt section 6.

This is the only vocabulary the model is allowed to produce. Anything that
doesn't fit one of these shapes is coerced to Unknown by parse_model_output,
so the phone app never has to guess what a malformed response meant.
"""

import json
import re
from datetime import datetime
from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, model_validator


class _Strict(BaseModel):
    """No extra fields allowed anywhere in the schema - an LLM that adds an
    unrequested field (e.g. "confidence") should fail validation and fall
    back to Unknown rather than silently being accepted."""

    model_config = ConfigDict(extra="forbid")


class OpenAppSlots(_Strict):
    app_name: str


class OpenAppIntent(_Strict):
    intent: Literal["OpenApp"]
    slots: OpenAppSlots


class CloseAppSlots(_Strict):
    app_name: str


class CloseAppIntent(_Strict):
    intent: Literal["CloseApp"]
    slots: CloseAppSlots


class CallSlots(_Strict):
    contact_name: str | None = None
    phone_number: str | None = None

    @model_validator(mode="after")
    def exactly_one_target(self) -> "CallSlots":
        if bool(self.contact_name) == bool(self.phone_number):
            raise ValueError("exactly one of contact_name or phone_number is required")
        return self


class CallIntent(_Strict):
    intent: Literal["Call"]
    slots: CallSlots


class CreateCalendarEventSlots(_Strict):
    title: str
    start_time: datetime
    end_time: datetime | None = None


class CreateCalendarEventIntent(_Strict):
    intent: Literal["CreateCalendarEvent"]
    slots: CreateCalendarEventSlots


class CreateReminderSlots(_Strict):
    title: str
    time: datetime


class CreateReminderIntent(_Strict):
    intent: Literal["CreateReminder"]
    slots: CreateReminderSlots


class UnknownSlots(_Strict):
    pass


class UnknownIntent(_Strict):
    intent: Literal["Unknown"]
    slots: UnknownSlots = UnknownSlots()


ParsedIntent = Annotated[
    Union[
        OpenAppIntent,
        CloseAppIntent,
        CallIntent,
        CreateCalendarEventIntent,
        CreateReminderIntent,
        UnknownIntent,
    ],
    Field(discriminator="intent"),
]

_adapter: TypeAdapter[ParsedIntent] = TypeAdapter(ParsedIntent)

UNKNOWN = UnknownIntent(intent="Unknown")

_JSON_FENCE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)


def _extract_json_text(raw: str) -> str:
    """Models sometimes wrap output in a markdown code fence despite instructions
    not to. Strip that before parsing, but don't try to salvage anything else."""
    match = _JSON_FENCE.search(raw)
    return match.group(1) if match else raw


def parse_model_output(raw: str) -> ParsedIntent:
    """Turn a raw model response into a validated intent, or Unknown.

    This is the deterministic boundary described in design.txt section 6:
    the model proposes, this function disposes. Nothing downstream of this
    ever sees anything outside the fixed schema.
    """
    try:
        text = _extract_json_text(raw)
        data = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return UNKNOWN

    try:
        return _adapter.validate_python(data)
    except Exception:
        return UNKNOWN
