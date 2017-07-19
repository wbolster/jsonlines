"""
Tests for the jsonlines library.
"""

import collections
import io
import jsonlines
import tempfile

import pytest


SAMPLE_BYTES = b'{"a": 1}\n{"b": 2}\n'
SAMPLE_TEXT = SAMPLE_BYTES.decode('utf-8')


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


def test_reading_from_iterable():
    with jsonlines.Reader(['1', b'{}']) as reader:
        assert list(reader) == [1, {}]
    assert 'wrapping <list at ' in repr(reader)


def test_writer_text():
    fp = io.StringIO()
    with jsonlines.Writer(fp) as writer:
        writer.write({'a': 1})
        writer.write({'b': 2})
    assert fp.getvalue() == SAMPLE_TEXT


def test_writer_binary():
    fp = io.BytesIO()
    with jsonlines.Writer(fp) as writer:
        writer.write_all([
            {'a': 1},
            {'b': 2},
        ])
    assert fp.getvalue() == SAMPLE_BYTES


def test_closing():
    reader = jsonlines.Reader([])
    reader.close()
    with pytest.raises(RuntimeError):
        reader.read()
    writer = jsonlines.Writer(io.BytesIO())
    writer.close()
    writer.close()  # no-op
    with pytest.raises(RuntimeError):
        writer.write(123)


def test_invalid_lines():
    data = u'[1, 2'
    with jsonlines.Reader(io.StringIO(data)) as reader:
        with pytest.raises(jsonlines.InvalidLineError) as excinfo:
            reader.read()
        exc = excinfo.value
        assert "invalid json" in str(exc)
        assert exc.line == data


def test_skip_invalid():
    fp = io.StringIO(u"12\ninvalid\n34")
    reader = jsonlines.Reader(fp)
    it = reader.iter(skip_invalid=True)
    assert next(it) == 12
    assert next(it) == 34


def test_empty_strings_in_iterable():
    input = ['123', '', '456']
    it = iter(jsonlines.Reader(input))
    assert next(it) == 123
    with pytest.raises(jsonlines.InvalidLineError):
        next(it)
    with pytest.raises(StopIteration):
        next(it)
    it = jsonlines.Reader(input).iter(skip_empty=True)
    assert list(it) == [123, 456]


def test_invalid_utf8():
    with jsonlines.Reader([b'\xff\xff']) as reader:
        with pytest.raises(jsonlines.InvalidLineError) as excinfo:
            reader.read()
        assert 'line is not valid utf-8' in str(excinfo.value)


def test_empty_lines():
    data_with_empty_line = b"1\n\n2\n"
    with jsonlines.Reader(io.BytesIO(data_with_empty_line)) as reader:
        assert reader.read()
        with pytest.raises(jsonlines.InvalidLineError):
            reader.read()
        assert reader.read() == 2
        with pytest.raises(EOFError):
            reader.read()
    with jsonlines.Reader(io.BytesIO(data_with_empty_line)) as reader:
        assert list(reader.iter(skip_empty=True)) == [1, 2]


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
        with pytest.raises(jsonlines.InvalidLineError) as excinfo:
            next(it)
        exc = excinfo.value
        assert "does not match requested type" in str(exc)


def test_writer_flags():
    fp = io.BytesIO()
    with jsonlines.Writer(fp, compact=True, sort_keys=True) as writer:
        writer.write(collections.OrderedDict([
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


def test_open_reading():
    with tempfile.NamedTemporaryFile("wb") as fp:
        fp.write(b"123\n")
        fp.flush()
        with jsonlines.open(fp.name) as reader:
            assert list(reader) == [123]


def test_open_writing():
    with tempfile.NamedTemporaryFile("w+b") as fp:
        with jsonlines.open(fp.name, mode='w') as writer:
            writer.write(123)
        assert fp.read() == b"123\n"
    assert fp.name in repr(writer)


def test_open_invalid_mode():
    with pytest.raises(ValueError) as excinfo:
        jsonlines.open('foo', mode='foo')
    assert 'mode' in str(excinfo.value)
