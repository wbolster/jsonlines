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
        pass


def make_text_fp(fp):
    return NonClosingTextIOWrapper(fp, encoding='UTF-8', line_buffering=True)


class Error(Exception):
    """Base error class."""
    pass


class InvalidLineError(Error):
    """Error raised when an invalid line is encountered."""
    def __init__(self, msg, value):
        self.value = value
        super(InvalidLineError, self).__init__(msg)


class ReaderWriterBase(object):

    def __init__(self, fp):
        self._fp = fp
        self._should_close_fp = False
        self._closed = False

    def _close(self):
        if self._closed:
            return
        if self._should_close_fp:
            self._fp.close()
        self._closed = True

    def __repr__(self):
        return '<jsonlines.{} fp={!r}'.format(
            self.__class__.__name__,
            self._fp)

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self._close()
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
        return next(self)

    def __iter__(self):
        return self

    def __next__(self):
        line = next(self._line_iter)
        assert isinstance(line, six.text_type)
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise InvalidLineError(
                "invalid json: {}".format(exc), line) from exc
        return value

    if six.PY2:  # pragma: no cover
        next = __next__


class Writer(ReaderWriterBase):
    def __init__(self, fp):
        super(Writer, self).__init__(fp)

        # Make sure the file-like object accepts unicode strings.
        try:
            fp.write(u'')
        except TypeError:
            self._text_fp = make_text_fp(fp)
            self._fp_binary = True
        else:
            self._text_fp = fp
            self._fp_binary = False

    def write(self, obj):
        line = json.dumps(obj, ensure_ascii=False)

        # On Python 2, the JSON module has the nasty habit of returning
        # either a byte string or unicode string, depending on whether
        # the serialised structure can be encoded using ASCII only.
        # However, io.TextIOWrapper only accepts unicode strings. To
        # avoid useless encode/decode overhead, write directly to
        # self_fp in case it was a binary stream to start with.
        if six.PY2 and self._fp_binary and isinstance(line, six.binary_type):
            self._fp.write(line)
            self._fp.write(b"\n")
            return

        # In all other cases, we simply write the unicode string to the file.
        assert isinstance(line, six.text_type)
        self._text_fp.write(line)
        self._text_fp.write(u"\n")


def open(name, mode='r'):

    if mode not in ('r', 'w'):
        raise ValueError("'mode' must be either 'r' or 'w'")

    mode += 't'
    fp = io.open(name, mode=mode, encoding='UTF-8')

    if mode == 'rt':
        instance = Reader(fp)
    elif mode == 'wt':
        instance = Writer(fp)

    instance._should_close_fp = True
    return instance
