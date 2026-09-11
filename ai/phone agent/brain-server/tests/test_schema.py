from brain.schema import UNKNOWN, parse_model_output


def test_open_app_valid():
    result = parse_model_output('{"intent": "OpenApp", "slots": {"app_name": "spotify"}}')
    assert result.intent == "OpenApp"
    assert result.slots.app_name == "spotify"


def test_close_app_valid():
    result = parse_model_output('{"intent": "CloseApp", "slots": {"app_name": "spotify"}}')
    assert result.intent == "CloseApp"


def test_call_with_contact_name():
    result = parse_model_output('{"intent": "Call", "slots": {"contact_name": "mom"}}')
    assert result.intent == "Call"
    assert result.slots.contact_name == "mom"
    assert result.slots.phone_number is None


def test_call_with_phone_number():
    result = parse_model_output('{"intent": "Call", "slots": {"phone_number": "+15551234567"}}')
    assert result.intent == "Call"
    assert result.slots.phone_number == "+15551234567"


def test_call_with_both_contact_and_number_is_unknown():
    result = parse_model_output(
        '{"intent": "Call", "slots": {"contact_name": "mom", "phone_number": "+15551234567"}}'
    )
    assert result == UNKNOWN


def test_call_with_neither_is_unknown():
    result = parse_model_output('{"intent": "Call", "slots": {}}')
    assert result == UNKNOWN


def test_create_calendar_event_valid():
    result = parse_model_output(
        '{"intent": "CreateCalendarEvent", "slots": '
        '{"title": "dentist", "start_time": "2026-09-11T15:00:00", "end_time": "2026-09-11T15:30:00"}}'
    )
    assert result.intent == "CreateCalendarEvent"
    assert result.slots.title == "dentist"


def test_create_calendar_event_without_end_time_valid():
    result = parse_model_output(
        '{"intent": "CreateCalendarEvent", "slots": {"title": "dentist", "start_time": "2026-09-11T15:00:00"}}'
    )
    assert result.intent == "CreateCalendarEvent"
    assert result.slots.end_time is None


def test_create_reminder_valid():
    result = parse_model_output(
        '{"intent": "CreateReminder", "slots": {"title": "take out trash", "time": "2026-09-10T18:00:00"}}'
    )
    assert result.intent == "CreateReminder"


def test_explicit_unknown():
    result = parse_model_output('{"intent": "Unknown", "slots": {}}')
    assert result == UNKNOWN


def test_missing_required_slot_is_unknown():
    result = parse_model_output('{"intent": "OpenApp", "slots": {}}')
    assert result == UNKNOWN


def test_unrecognized_intent_name_is_unknown():
    result = parse_model_output('{"intent": "DeleteEverything", "slots": {}}')
    assert result == UNKNOWN


def test_malformed_json_is_unknown():
    result = parse_model_output("not json at all")
    assert result == UNKNOWN


def test_markdown_fenced_json_is_still_parsed():
    result = parse_model_output(
        '```json\n{"intent": "OpenApp", "slots": {"app_name": "spotify"}}\n```'
    )
    assert result.intent == "OpenApp"


def test_extra_unexpected_top_level_field_is_unknown():
    result = parse_model_output(
        '{"intent": "OpenApp", "slots": {"app_name": "spotify"}, "confidence": 0.9}'
    )
    assert result == UNKNOWN
