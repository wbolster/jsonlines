=========
jsonlines
=========

.. py:currentmodule:: jsonlines

``jsonlines`` is a Python library to simplify working with jsonlines_
and ndjson_ data.

.. _jsonlines: http://jsonlines.org/
.. _ndjson: http://ndjson.org/

This data format is straight-forward: it is simply one valid JSON
value per line, encoded using UTF-8. While code to consume and create
such data is not that complex, it quickly becomes non-trivial enough
to warrant a dedicated library when adding data validation, error
handling, support for both binary and text streams, and so on. This
small library implements all that (and more!) so that applications
using this format do not have to reinvent the wheel.


Features
========

* Convenient :py:func:`~jsonlines.open()` function

  * makes simple cases trivial to write
  * takes a file name and a mode
  * returns either a :py:class:`~jsonlines.Reader` or
    :py:class:`~jsonlines.Writer` instance
  * can be used as a context manager

* Flexible :py:class:`~jsonlines.Reader`

  * wraps a file-like object or any other iterable yielding lines
  * can read lines directly via the
    :py:meth:`~jsonlines.Reader.read()` method
  * can be used as an iterator, either directly or via the
    :py:meth:`~jsonlines.Reader.iter()` method
  * can validate data types, including `None` checks
  * can skip invalid lines during iteration
  * provides decent error messages
  * can be used as a context manager
  * allows complete control over decoding using a custom ``loads``
    callable

* Flexible :py:class:`~jsonlines.Writer`

  * wraps a file-like object
  * can produce compact output
  * can sort keys (deterministic output)
  * can flush the underlying stream after each write
  * can be used as a context manager
  * allows complete control over encoding using a custom ``dumps``
    callable


Installation
============

::

  pip install jsonlines

The supported Python versions are 3.7+.


User guide
==========

Import the ``jsonlines`` module to get started:

.. code-block:: python

    import jsonlines


The convenience function :py:func:`jsonlines.open()` takes a file name
and returns either a reader or writer, making simple cases extremely
simple::

  with jsonlines.open('input.jsonl') as reader:
      for obj in reader:
          ...

  with jsonlines.open('output.jsonl', mode='w') as writer:
      writer.write(...)

A :py:class:`Reader` typically wraps a file-like object::

  fp = io.BytesIO(...)  # readable file-like object
  reader = jsonlines.Reader(fp)
  first = reader.read()
  second = reader.read()
  reader.close()
  fp.close()

Instead of a file-like object, any iterable yielding JSON encoded
strings can be provided::

  lines = ['1', '2', '3']
  reader = jsonlines.Reader(lines)

While the :py:meth:`Reader.read` method can be used directly, it is
often more convenient to use iteration::

  for obj in reader:
      ...

Custom iteration flags, such as type checks, can be specified by
calling :py:meth:`Reader.iter()` instead::

  for obj in reader.iter(type=dict, skip_invalid=True):
      ...

A :py:class:`Writer` wraps a file-like object, and can write a single
object, or multiple objects at once::

  fp = io.BytesIO()  # writable file-like object
  writer = jsonlines.Writer(fp)
  writer.write(...)
  writer.write_all([
      ...,
      ...,
      ...,
  ])
  writer.close()
  fp.close()

Both readers and writers can be used as a context manager, in which
case they will be closed automatically. Note that this will not close
a passed-in file-like object since that object’s life span is
controlled by the calling code. Example::

  fp = io.BytesIO()  # file-like object
  with jsonlines.Writer(fp) as writer:
      writer.write(...)
  fp.close()

Note that the :py:func:`jsonlines.open()` function *does* close the
opened file, since the open file is not explicitly opened by the
calling code. That means no ``.close()`` is needed there::

  with jsonlines.open('input.jsonl') as reader:
      ...

This should be enough to get started. See the API docs below for
more details.


API
===

.. autofunction:: jsonlines.open

.. autoclass:: jsonlines.Reader
   :members:
   :inherited-members:

.. autoclass:: jsonlines.Writer
   :members:
   :inherited-members:

.. autoclass:: jsonlines.Error
   :members:

.. autoclass:: jsonlines.InvalidLineError
   :members:


Contributing
============

The source code and issue tracker for this package can be found on GitHub:

  https://github.com/wbolster/jsonlines


Version history
===============

* 4.0.0, released at ...

  * drop support for end-of-life Python versions; this package is now
    Python 3.7+ only.
    (`#80 <https://github.com/wbolster/jsonlines/pull/80>`_)

* 3.1.0, released at 2022-07-01

  * Return number of chars/bytes written by :py:meth:`Writer.write()`
    and :py:meth:`~Writer.write_all()`
    (`#73 <https://github.com/wbolster/jsonlines/pull/73>`_)

  * allow ``mode='x'`` in :py:func:`~jsonlines.open()`
    to open a file for exclusive creation
    (`#74 <https://github.com/wbolster/jsonlines/issues/74>`_)

* 3.0.0, released at 2021-12-04

  * add type annotations; adopt mypy in strict mode
    (`#58 <https://github.com/wbolster/jsonlines/pull/58>`_,
    `#62 <https://github.com/wbolster/jsonlines/pull/62>`_)

  * ignore UTF-8 BOM sequences in various scenarios
    (`#69 <https://github.com/wbolster/jsonlines/pull/69>`_)

  * support ``dumps()`` callables returning bytes again
    (`#64 <https://github.com/wbolster/jsonlines/issues/64>`_)

  * add basic support for rfc7464 text sequences
    (`#61 <https://github.com/wbolster/jsonlines/pull/61>`_)

  * drop support for ``numbers.Number`` in ``type=`` arguments
    (`#63 <https://github.com/wbolster/jsonlines/issues/63>`_)

* 2.0.0, released at 2021-01-04

  * drop support for end-of-life Python versions; this package is now
    Python 3.6+ only.
    (`#54 <https://github.com/wbolster/jsonlines/pull/54>`_,
    `#51 <https://github.com/wbolster/jsonlines/pull/51>`_)

* 1.2.0, released at 2017-08-17

  * allow ``mode='a'`` in :py:func:`~jsonlines.open()`
    to allow appending to an existing file
    (`#31 <https://github.com/wbolster/jsonlines/pull/31>`_)

* 1.1.3, released at 2017-07-19

  * fix incomplete iteration when given list containing empty strings
    (`#30 <https://github.com/wbolster/jsonlines/issues/30>`_)

* 1.1.2, released at 2017-06-26

  * documentation tweaks
  * enable building universal wheels

* 1.1.1, released at 2017-06-04

  * include licensing information in sdist
    (`#27 <https://github.com/wbolster/jsonlines/issues/27>`_)
  * doc tweaks

* 1.1.0, released at 2016-10-07

  * rename first argument to :py:class:`Reader` since it is not
    required to be a file-like object
  * actually check that the reader/writer is not closed when
    performing operations
  * improved `repr()` output
  * doc tweaks

* 1.0.0, released at 2016-10-05

  * minimum Python versions are Python 3.4+ and Python 2.7+
  * implemented lots of configuration options
  * add proper exceptions handling
  * add proper documentation
  * switch to semver


* 0.0.1, released at 2015-03-02

  * initial release with basic functionality


License
=======

.. include:: ../LICENSE.rst
