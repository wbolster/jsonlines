=========
jsonlines
=========

This is a Python library to simplify working with *jsonlines* data.

The *jsonlines* file format is very straight-forward: it's simply a UTF-8
encoded text file with one JSON value per line. See http://jsonlines.org/ for
details.


Features
========

* ``jsonlines.open()`` convenience helper

* reader (``jsonlines.Reader``)

  * iterable
  * decent error messages
  * supports custom ``loads`` callable

* writer (``jsonlines.Writer``)

  * optionally sorts keys
  * optionally produces compact output
  * supports custom ``dumps`` callable


Installation
============

::

  pip install jsonlines


Usage
=====

Import the ``jsonlines`` module to get started:

.. code-block:: python

    import jsonlines


open()
------

The convenience function ``jsonlines.open()`` takes a file name and
returns either a reader or writer, making simple cases extremely
simple:

.. code-block:: python

    with jsonlines.open('input.jsonl') as reader:
        for obj in reader:
            print(obj)

    with jsonlines.open('output.jsonl', mode='w') as writer:
        writer.write({"a": 1})
        writer.write({"b": 2})


Reader
------

A ``Reader`` wraps a file-like object. Basic usage:

.. code-block:: python

    fp = io.BytesIO(...)  # readable file-like object
    reader = jsonlines.Reader(fp)
    first = reader.read()
    second = reader.read()
    reader.close()
    fp.close()

Readers are iterable:

.. code-block:: python

    for obj in reader:
        ...

Custom iteration flags can be specified by using ``Reader.iter()`` instead:

.. code-block:: python

    for obj in reader.iter(type=dict, skip_invalid=True):
        ...


Writer
------

A ``Writer`` wraps a file-like object. Basic usage:

.. code-block:: python

    fp = io.BytesIO()  # writable file-like object
    writer = jsonlines.Writer(fp)
    writer.write([1, 2, 3])
    writer.write([4, 5, 6])
    list_of_objects = [
        [7, 8, 9],
        [10, 11, 12],
    ]
    writer.write_all(list_of_objects)
    writer.close()
    fp.close()


Context manager
---------------

Both readers and writers can be used as a context manager, in which
case they will be closed automatically. Note that this does not close
the passed-in file-like object since that object‘s life span is
controlled by the calling code:

.. code-block:: python

    fp = io.BytesIO()
    with jsonlines.Writer(fp) as writer:
        writer.write(...)
    fp.close()

Note that the ``jsonlines.open()`` convenience function *does* close
the opened file, since the open file is not explicitly opened by the
calling code. That means no ``.close()`` is needed there:

.. code-block:: python

    with jsonlines.open('input.jsonl') as reader:
        ...


More
----

Until this project has proper documentation, see the docstrings in
the code and the tests for some more details and examples.


License
=======

BSD.


Contributing
============

Feel free to contribute to this project by opening issues.
