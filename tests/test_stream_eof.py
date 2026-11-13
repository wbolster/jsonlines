import gzip
import io
from typing import NoReturn

import pytest

import jsonlines


@pytest.mark.parametrize("skip_invalid", [False, True])
def test_truncated_gzip_is_not_clean_eof(skip_invalid: bool) -> None:
    payload = gzip.compress(b'{"value": 1}\n')[:-8]
    with gzip.GzipFile(fileobj=io.BytesIO(payload)) as stream:
        reader = jsonlines.Reader(stream)
        with pytest.raises(EOFError, match="end-of-stream"):
            list(reader.iter(skip_invalid=skip_invalid))


def test_decoder_eof_error_is_not_swallowed() -> None:
    def loads(line: object) -> NoReturn:
        raise EOFError("decoder failure")

    reader = jsonlines.Reader(["{}\n"], loads=loads)
    with pytest.raises(EOFError, match="decoder failure"):
        list(reader)


def test_clean_eof_preserves_public_contract() -> None:
    reader = jsonlines.Reader([])
    with pytest.raises(EOFError):
        reader.read()
    assert list(jsonlines.Reader([])) == []
