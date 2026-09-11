import time
from datetime import datetime, timezone

from fastapi import FastAPI
from pydantic import BaseModel

from brain.logging_config import configure_logging
from brain.model_client import call_model, warm_up
from brain.schema import ParsedIntent, parse_model_output

logger = configure_logging()
app = FastAPI()


@app.on_event("startup")
def _warm_up_model() -> None:
    logger.info("warming up model...")
    started = time.perf_counter()
    try:
        warm_up()
        logger.info("model warm-up done in %.1fs", time.perf_counter() - started)
    except Exception:
        logger.exception("model warm-up failed (is ollama running?)")


class ParseRequest(BaseModel):
    text: str


@app.post("/parse-intent")
def parse_intent(request: ParseRequest) -> ParsedIntent:
    now_iso = datetime.now(timezone.utc).astimezone().isoformat()
    logger.info("request text=%r", request.text)

    started = time.perf_counter()
    raw = call_model(request.text, now_iso)
    elapsed = time.perf_counter() - started
    parsed = parse_model_output(raw)

    logger.info("response raw=%r parsed=%s elapsed=%.2fs", raw, parsed.model_dump(), elapsed)
    return parsed


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
