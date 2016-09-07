
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
    data = u'[1, 2'
    reader = jsonlines.Reader(io.StringIO(data))
    with pytest.raises(jsonlines.InvalidLineError) as excinfo:
        reader.read()
    exc = excinfo.value
    assert str(exc).startswith("invalid json")
    assert exc.value == data


def test_typed_reads():
    reader = jsonlines.Reader(io.StringIO(u'12\n"foo"'))
    assert reader.read_int() == 12
    with pytest.raises(jsonlines.InvalidLineError) as excinfo:
        reader.read_int()
    exc = excinfo.value
    assert "does not match requested type" in str(exc)
    assert exc.value == "foo"


# TODO: jsonlines.open() in a tmpdir


def test_invalid_mode():

    with pytest.raises(ValueError) as exc:
        jsonlines.open('foo', mode='foo')
    assert 'mode' in str(exc.value)
