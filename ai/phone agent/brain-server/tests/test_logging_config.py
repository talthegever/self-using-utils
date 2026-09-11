import logging
import logging.handlers

import pytest

from brain import logging_config


@pytest.fixture(autouse=True)
def _reset_brain_logger():
    # "brain" is a process-wide named logger - configure_logging() is
    # idempotent by design (see its `if logger.handlers: return logger`
    # guard), which would otherwise leak handlers/paths across these tests.
    logger = logging.getLogger("brain")
    logger.handlers = []
    yield
    logger.handlers = []


def _point_at(monkeypatch, tmp_path):
    log_dir = tmp_path / "logs"
    log_file = log_dir / "server.log"
    monkeypatch.setattr(logging_config, "LOG_DIR", log_dir)
    monkeypatch.setattr(logging_config, "LOG_FILE", log_file)
    return log_dir, log_file


def test_creates_log_dir_and_file(tmp_path, monkeypatch):
    log_dir, log_file = _point_at(monkeypatch, tmp_path)

    logger = logging_config.configure_logging()
    logger.info("hello")
    for h in logger.handlers:
        h.flush()

    assert log_dir.exists()
    assert log_file.exists()


def test_has_one_console_and_one_utf8_file_handler(tmp_path, monkeypatch):
    _point_at(monkeypatch, tmp_path)

    logger = logging_config.configure_logging()

    console_handlers = [h for h in logger.handlers if type(h) is logging.StreamHandler]
    file_handlers = [
        h for h in logger.handlers if isinstance(h, logging.handlers.RotatingFileHandler)
    ]
    assert len(console_handlers) == 1
    assert len(file_handlers) == 1
    assert file_handlers[0].encoding == "utf-8"


def test_configure_logging_is_idempotent(tmp_path, monkeypatch):
    _point_at(monkeypatch, tmp_path)

    logger1 = logging_config.configure_logging()
    handler_count = len(logger1.handlers)
    logger2 = logging_config.configure_logging()

    assert logger1 is logger2
    assert len(logger2.handlers) == handler_count


def test_hebrew_text_round_trips_correctly(tmp_path, monkeypatch):
    # Regression test for the mojibake bug seen this session: without an
    # explicit utf-8 encoding, Windows' default file encoding mangled
    # Hebrew log lines into replacement characters.
    _, log_file = _point_at(monkeypatch, tmp_path)

    logger = logging_config.configure_logging()
    hebrew_text = "פתח את כרום"
    logger.info("request text=%r", hebrew_text)
    for h in logger.handlers:
        h.flush()

    content = log_file.read_text(encoding="utf-8")
    assert hebrew_text in content
