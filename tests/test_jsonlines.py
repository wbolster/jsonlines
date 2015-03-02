
import io
import jsonlines

import pytest


SAMPLE_BYTES = b'{"a": 1}\n{"b": 2}\n'


def test_reader():
    fp = io.BytesIO(SAMPLE_BYTES)
    reader = jsonlines.Reader(fp)
    it = iter(reader)
    assert next(it) == {'a': 1}
    assert next(it) == {'b': 2}
    with pytest.raises(StopIteration):
        next(it)


def test_writer():
    fp = io.BytesIO()
    writer = jsonlines.Writer(fp)
    writer.dump({'a': 1})
    writer.dump({'b': 2})
    assert fp.getvalue() == SAMPLE_BYTES


# TODO: jsonlines.open() in a tmpdir


def test_invalid_mode():

    with pytest.raises(ValueError) as exc:
        jsonlines.open('foo', mode='foo')
    assert 'mode' in str(exc.value)
