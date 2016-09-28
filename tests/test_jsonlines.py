"""
Tests for the jsonlines library.
"""

import io
import jsonlines

from collections import OrderedDict

import pytest


SAMPLE_BYTES = b'{"a": 1}\n{"b": 2}\n'


def test_reader():
    fp = io.BytesIO(SAMPLE_BYTES)
    with jsonlines.Reader(fp) as reader:
        it = iter(reader)
        assert next(it) == {'a': 1}
        assert next(it) == {'b': 2}
        with pytest.raises(StopIteration):
            next(it)
        with pytest.raises(EOFError):
            reader.read()
    assert reader.closed


def test_writer():
    fp = io.BytesIO()
    with jsonlines.Writer(fp) as writer:
        writer.write({'a': 1})
        writer.write({'b': 2})
    assert fp.getvalue() == SAMPLE_BYTES
    assert writer.closed


def test_invalid_lines():
    data = u'[1, 2'
    with jsonlines.Reader(io.StringIO(data)) as reader:
        with pytest.raises(jsonlines.InvalidLineError) as excinfo:
            reader.read()
        exc = excinfo.value
        assert str(exc).startswith("invalid json")
        assert exc.line == data


def test_skip_invalid():
    fp = io.StringIO(u"12\ninvalid\n34")
    reader = jsonlines.Reader(fp)
    it = reader.iter(skip_invalid=True)
    assert next(it) == 12
    assert next(it) == 34


def test_typed_reads():
    with jsonlines.Reader(io.StringIO(u'12\n"foo"\n')) as reader:
        assert reader.read(type=int) == 12
        with pytest.raises(jsonlines.InvalidLineError) as excinfo:
            reader.read(type=float)
        exc = excinfo.value
        assert "does not match requested type" in str(exc)
        assert exc.line == '"foo"'


def test_typed_iteration():
    fp = io.StringIO(u'1\n2\n')
    with jsonlines.Reader(fp) as reader:
        actual = list(reader.iter(type=int))
        assert actual == [1, 2]

    fp = io.StringIO(u'1\n2\n')
    with jsonlines.Reader(fp) as reader:
        it = reader.iter(type=str)
        with pytest.raises(jsonlines.InvalidLineError):
            next(it)


def test_writer_flags():
    fp = io.BytesIO()
    with jsonlines.Writer(fp, compact=True, sort_keys=True) as writer:
        writer.write(OrderedDict([
            ('b', 2),
            ('a', 1),
        ]))
    assert fp.getvalue() == b'{"a":1,"b":2}\n'


def test_custom_dumps():
    fp = io.BytesIO()
    writer = jsonlines.Writer(fp, dumps=lambda obj: 'oh hai')
    with writer:
        writer.write({})
    assert fp.getvalue() == b'oh hai\n'


def test_custom_loads():
    fp = io.BytesIO(b"{}\n")
    with jsonlines.Reader(fp, loads=lambda s: 'uh what') as reader:
        assert reader.read() == 'uh what'

# TODO: jsonlines.open() in a tmpdir


def test_invalid_mode():
    with pytest.raises(ValueError) as excinfo:
        jsonlines.open('foo', mode='foo')
    assert 'mode' in str(excinfo.value)
