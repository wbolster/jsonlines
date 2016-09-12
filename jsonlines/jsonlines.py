"""
jsonlines implementation
"""

import io
import json

import six


class NonClosingTextIOWrapper(io.TextIOWrapper):
    """
    Text IO wrapper subclass that doesn't close the underlying stream.
    """
    def __del__(self):
        try:
            self.flush()
            self.detach()
        except Exception:
            pass

    def close(self):
        # Override TextIOWrapper.close() since it will also
        # unconditionally .close() the underlying stream, which we do
        # not want.
        self.flush()
        self.detach()


def make_text_fp(fp):
    return NonClosingTextIOWrapper(fp, encoding='utf-8')


class Error(Exception):
    """Base error class."""
    pass


class InvalidLineError(Error):
    """Error raised when an invalid line is encountered."""
    def __init__(self, msg, value):
        self.value = value
        super(InvalidLineError, self).__init__(msg)


class ReaderWriterBase(object):
    """
    Base class with shared behaviour for both the reader and writer.
    """

    #: Whether this reader/writer is closed.
    closed = False

    def __init__(self, fp):
        self._fp = self._text_fp = fp
        self._should_close_fp = False
        self.closed = False

    def close(self):
        """
        Close this reader/writer.

        This closes the underlying file if that file has been opened by
        this reader/writer. When an already opened file-like object was
        provided, the caller is responsible for closing it.
        """
        if self.closed:
            return
        self.closed = True
        if self._fp is not self._text_fp:
            self._text_fp.close()
        if self._should_close_fp:
            self._fp.close()

    def __repr__(self):
        return '<jsonlines.{} fp={!r}'.format(
            type(self).__name__,
            self._fp)

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()
        return False


class Reader(ReaderWriterBase):
    def __init__(self, fp):
        super(Reader, self).__init__(fp)

        # Make sure the file-like object returns unicode strings.
        if isinstance(fp.read(0), six.text_type):
            text_fp = fp
        else:
            text_fp = make_text_fp(fp)

        self._line_iter = iter(text_fp)

    def read(self):
        """Read a single line."""
        line = next(self._line_iter)
        assert isinstance(line, six.text_type)
        try:
            value = json.loads(line)
        except ValueError as exc:
            six.raise_from(
                InvalidLineError("invalid json: {}".format(exc), line),
                exc)
        return value

    def read_string(self, allow_none=False):
        """Read a single line containing a string."""
        value = self.read()
        if value is None and allow_none:
            return None
        if not isinstance(value, six.text_type):
            raise InvalidLineError("line does not match requested type", value)
        return value

    def read_int(self, allow_none=False):
        """Read a single line containing an integer."""
        value = self.read()
        if value is None and allow_none:
            return None
        if isinstance(value, bool) or not isinstance(value, six.integer_types):
            raise InvalidLineError("line does not match requested type", value)
        return value

    def read_float(self, allow_none=False):
        """Read a single line containing a float."""
        value = self.read()
        if value is None and allow_none:
            return None
        if not isinstance(value, float):
            raise InvalidLineError("line does not match requested type", value)
        return value

    def read_number(self, allow_none=False):
        """Read a single line containing a number."""
        value = self.read()
        if value is None and allow_none:
            return None
        if isinstance(value, bool) or not isinstance(
                value, six.integer_types + (float,)):
            raise InvalidLineError("line does not match requested type", value)
        return value

    def read_bool(self, allow_none=False):
        """Read a single line containing a boolean."""
        value = self.read()
        if value is None and allow_none:
            return None
        if not isinstance(value, bool):
            raise InvalidLineError("line does not match requested type", value)
        return value

    def read_dict(self, allow_none=False):
        """Read a single line containing a dict (JSON object)."""
        value = self.read()
        if value is None and allow_none:
            return None
        if not isinstance(value, dict):
            raise InvalidLineError("line does not match requested type", value)
        return value

    def read_list(self, allow_none=False):
        """Read a single line containing a list (JSON array)."""
        value = self.read()
        if value is None and allow_none:
            return None
        if not isinstance(value, (tuple, list)):
            raise InvalidLineError("line does not match requested type", value)
        return value

    def __iter__(self):
        return self

    def __next__(self):
        return self.read()

    if six.PY2:  # pragma: no cover
        next = __next__


class Writer(ReaderWriterBase):
    """
    Writer for the jsonlines format.
    """
    def __init__(self, fp, flush=False):
        super(Writer, self).__init__(fp)
        self._flush = flush
        try:
            fp.write(u'')
        except TypeError:
            self._text_fp = make_text_fp(fp)
            self._fp_is_binary = True
        else:
            self._text_fp = fp
            self._fp_is_binary = False

    def write(self, obj):
        line = json.dumps(obj, ensure_ascii=False)
        written = False
        if six.PY2 and isinstance(line, six.binary_type):
            # On Python 2, the JSON module has the nasty habit of
            # returning either a byte string or unicode string,
            # depending on whether the serialised structure can be
            # encoded using ASCII only. However, text streams (including
            # io.TextIOWrapper) only accept unicode strings. To avoid
            # useless encode/decode overhead, write directly to the
            # file-like object if it was a binary stream (and hence
            # will accepts bytes).
            if self._fp_is_binary:
                self._fp.write(line)
                self._fp.write(b"\n")
                written = True
            else:
                line = line.decode('utf-8')
        if not written:
            assert isinstance(line, six.text_type)
            self._text_fp.write(line)
            self._text_fp.write(u"\n")
        if self._flush:
            self._text_fp.flush()


def open(name, mode='r', flush=False):
    if mode not in {'r', 'w'}:
        raise ValueError("'mode' must be either 'r' or 'w'")
    fp = io.open(name, mode=mode + 't', encoding='utf-8')
    if mode == 'r':
        instance = Reader(fp)
    else:
        instance = Writer(fp, flush=flush)
    instance._should_close_fp = True
    return instance
