"""
jsonlines implementation
"""

import abc
import numbers
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


class InvalidJsonArguments(Error):
    """
    Error raised when a pass-through argument to the JSON decoder/encoder is
    not supported by the jsonl format.
    """
    pass


class InvalidLineError(Error):
    """
    Error raised when an invalid line is encountered.

    This happens when the line does not contain valid JSON, or if a
    specific data type has been requested, and the line contained a
    different data type.
    """
    def __init__(self, msg, value):
        self.value = value
        super(InvalidLineError, self).__init__(msg)


class ReaderWriterBase(object):
    """
    Base class with shared behaviour for both the reader and writer.
    """

    #: Whether this reader/writer is closed.
    closed = False

    def __init__(self, fp, **json_kwargs):
        self._validate_json_kwargs(**json_kwargs)

        self._fp = self._text_fp = fp
        self._should_close_fp = False
        self._json_kwargs = json_kwargs
        self.closed = False

    @abc.abstractmethod
    def _validate_json_kwargs(self, **json_kwargs):
        """
        Validate that the pass-through arguments to the JSON decoder or encoder
        are supported by the jsonl format.

        :raises: InvalidJsonArguments if one of the arguments is invalid
        """
        raise NotImplementedError

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
    """
    Reader for the jsonlines format.
    """
    def __init__(self, fp, **json_kwargs):
        super(Reader, self).__init__(fp, **json_kwargs)
        if isinstance(fp.read(0), six.text_type):
            self._text_fp = fp
        else:
            self._text_fp = make_text_fp(fp)

    def _validate_json_kwargs(self, **json_kwargs):
        pass

    def read(self, allow_none=True):
        """Read a single line."""
        line = self._text_fp.readline()
        if not line:
            raise EOFError
        assert isinstance(line, six.text_type)
        try:
            value = json.loads(line, **self._json_kwargs)
        except ValueError as exc:
            six.raise_from(
                InvalidLineError("invalid json: {}".format(exc), line),
                exc)
        if value is None and not allow_none:
            raise InvalidLineError("line contained null value", line)
        return value

    def read_dict(self, allow_none=False):
        """Read a single line containing a dict (JSON object)."""
        value = self.read(allow_none=allow_none)
        if value is None:
            return None
        if not isinstance(value, dict):
            raise InvalidLineError("line does not match requested type", value)
        return value

    def read_list(self, allow_none=False):
        """Read a single line containing a list (JSON array)."""
        value = self.read(allow_none=allow_none)
        if value is None:
            return None
        if not isinstance(value, (tuple, list)):
            raise InvalidLineError("line does not match requested type", value)
        return value

    def read_string(self, allow_none=False):
        """Read a single line containing a string."""
        value = self.read(allow_none=allow_none)
        if value is None:
            return None
        if not isinstance(value, six.text_type):
            raise InvalidLineError("line does not match requested type", value)
        return value

    def read_int(self, allow_none=False):
        """Read a single line containing an integer."""
        value = self.read(allow_none=allow_none)
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, six.integer_types):
            raise InvalidLineError("line does not match requested type", value)
        return value

    def read_float(self, allow_none=False):
        """Read a single line containing a float."""
        value = self.read(allow_none=allow_none)
        if value is None:
            return None
        if not isinstance(value, float):
            raise InvalidLineError("line does not match requested type", value)
        return value

    def read_number(self, allow_none=False):
        """Read a single line containing a number."""
        value = self.read(allow_none=allow_none)
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, numbers.Number):
            raise InvalidLineError("line does not match requested type", value)
        return value

    def read_bool(self, allow_none=False):
        """Read a single line containing a boolean."""
        value = self.read(allow_none=allow_none)
        if value is None:
            return None
        if not isinstance(value, bool):
            raise InvalidLineError("line does not match requested type", value)
        return value

    def iter(self, type=None, allow_none=False, skip_invalid=False):
        """
        Iterate over all lines.

        If no arguments are specified, this is the same as directly
        iterating over this ``Reader`` instance.

        When specified, the `type` argument specifies the expected data
        types produced by the underlying file-like object. This is
        equivalent to repeatedly calling ``reader.read_xyz()``, e.g.
        :py:meth:`~Reader.read_int()`. Supported types are ``dict``,
        ``list``, ``str``, ``int``, ``float``, ``numbers.Number``, or
        ``bool``.

        The `allow_none` argument specifies whether ``None`` (``null``
        in JSON) is considered a valid value. If omitted, iteration will
        only yield ``None`` values if no type is specified.
        """
        if type is None:
            read = self.read
        elif type is dict:
            read = self.read_dict
        elif type is list:
            read = self.read_list
        elif type is str:
            read = self.read_string
        elif type is int:
            read = self.read_int
        elif type is float:
            read = self.read_float
        elif type is numbers.Number:
            read = self.read_number
        elif type is bool:
            read = self.read_bool
        else:
            raise ValueError("invalid type specified")
        if allow_none is None:
            allow_none = (type is None)
        try:
            if skip_invalid:
                while True:
                    try:
                        yield read(allow_none=allow_none)
                    except InvalidLineError:
                        pass
            else:
                while True:
                    yield read(allow_none=allow_none)
        except EOFError:
            pass

    def __iter__(self):
        return self.iter()


class Writer(ReaderWriterBase):
    """
    Writer for the jsonlines format.
    """
    def __init__(self, fp, flush=False, **json_kwargs):
        super(Writer, self).__init__(fp, **json_kwargs)
        self._flush = flush
        try:
            fp.write(u'')
        except TypeError:
            self._text_fp = make_text_fp(fp)
            self._fp_is_binary = True
        else:
            self._text_fp = fp
            self._fp_is_binary = False

    def _validate_json_kwargs(self, **json_kwargs):
        indent = json_kwargs.get('indent')
        if indent is not None:
            raise InvalidJsonArguments('indent argument not supported')

        separators = json_kwargs.get('separators', [])
        if any('\n' in separator for separator in separators):
            raise InvalidJsonArguments('newlines in separators not supported')

    def write(self, obj):
        self._json_kwargs.setdefault('ensure_ascii', False)
        line = json.dumps(obj, **self._json_kwargs)
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


def open(name, mode='r', flush=False, **json_kwargs):
    """
    :param json_kwargs: pass-through arguments to the json module

    """
    if mode not in {'r', 'w'}:
        raise ValueError("'mode' must be either 'r' or 'w'")
    fp = io.open(name, mode=mode + 't', encoding='utf-8')
    if mode == 'r':
        instance = Reader(fp, **json_kwargs)
    else:
        instance = Writer(fp, flush=flush, **json_kwargs)
    instance._should_close_fp = True
    return instance
