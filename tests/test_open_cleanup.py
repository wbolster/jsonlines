"""The open helper owns its stream even if wrapper construction fails."""

from pathlib import Path
from typing import Any

import jsonlines
import pytest


@pytest.mark.parametrize("mode", ["r", "w", "a", "x"])
def test_open_closes_stream_on_invalid_options(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:
    # Retain the real stream so garbage collection cannot hide a missed close.
    with (tmp_path / "data.jsonl").open("w+") as stream:
        monkeypatch.setattr(
            "jsonlines.jsonlines.builtins.open", lambda *a, **kw: stream
        )
        options: Any = {"compact": True} if mode == "r" else {"loads": lambda s: s}
        with pytest.raises(TypeError):
            jsonlines.open("unused.jsonl", mode=mode, **options)
        assert stream.closed


@pytest.mark.parametrize("error", [ValueError("encoder failed"), KeyboardInterrupt()])
def test_open_closes_stream_on_encoder_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, error: BaseException
) -> None:
    def dumps(obj: Any) -> str:
        raise error

    with (tmp_path / "data.jsonl").open("w+") as stream:
        monkeypatch.setattr(
            "jsonlines.jsonlines.builtins.open", lambda *a, **kw: stream
        )
        with pytest.raises(type(error)) as excinfo:
            jsonlines.open("unused.jsonl", mode="w", dumps=dumps)
        assert excinfo.value is error
        assert stream.closed
