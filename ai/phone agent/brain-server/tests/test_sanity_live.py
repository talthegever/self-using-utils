"""One opt-in test that actually calls the local Ollama model, to confirm
the full pipe works: server -> ollama -> schema-valid JSON.

Per design.txt / the grilling session: we don't try to test the model's
judgment with a big matrix of phrasings (that's not deterministic and not
really testable) - this is just a pipeline smoke test.

Run explicitly with: pytest -m live
Requires: ollama running locally with the model in brain/model_client.py
already pulled (see design.txt section 9).
"""

import pytest

from brain.schema import parse_model_output
from brain.model_client import call_model


@pytest.mark.live
def test_live_model_produces_schema_valid_output():
    raw = call_model("open spotify", now_iso="2026-09-10T12:00:00+00:00")
    parsed = parse_model_output(raw)

    assert parsed.intent == "OpenApp"
    assert parsed.slots.app_name.lower() == "spotify"
