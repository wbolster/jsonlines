
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
    writer.write({'a': 1})
    writer.write({'b': 2})
    assert fp.getvalue() == SAMPLE_BYTES


def test_invalid_lines():
    s = '[1, 2'
    r = jsonlines.Reader(io.StringIO(s))
    with pytest.raises(jsonlines.InvalidLineError) as excinfo:
        r.read()
    exc = excinfo.value
    assert str(exc).startswith("invalid json")
    assert exc.value == s


# TODO: jsonlines.open() in a tmpdir


def test_invalid_mode():

    with pytest.raises(ValueError) as exc:
        jsonlines.open('foo', mode='foo')
    assert 'mode' in str(exc.value)
