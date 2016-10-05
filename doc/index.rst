=========
jsonlines
=========

.. py:currentmodule:: jsonlines

``jsonlines`` is a Python library to simplify working with jsonlines_ data.

.. _jsonlines: http://jsonlines.org/

The *jsonlines* file format is very straight-forward: it's simply a UTF-8
encoded text file with one JSON value per line.


Features
========

* Convenience :py:func:`jsonlines.open()` function

  * makes simple cases trivial to write
  * takes a file name and a mode
  * returns either a :py:class:`~jsonlines.Reader` or
    :py:class:`~jsonlines.Writer` instance
  * can be used as a context manager

* Flexible reader (:py:class:`jsonlines.Reader`)

  * wraps a file-like object
  * can read lines directly via the
    :py:meth:`~jsonlines.Reader.read()` method
  * can be used as an iterator, either directly or via the
    :py:meth:`~jsonlines.Reader.iter()` method
  * can validate data types, including `None` checks
  * can skip invalid lines during iteration
  * provides decent error messages
  * can be used as a context manager

* Flexible writer (:py:class:`jsonlines.Writer`)

  * wraps a file-like object
  * can produce compact output
  * can sort keys (deterministic output)
  * can flush the underlying stream after each write
  * can be used as a context manager

* Both JSON encoding and decoding behaviour is fully configurable via
  custom ``dumps`` and ``loads`` callables.


Installation
============

::

  pip install jsonlines


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


A :py:class:`Reader` wraps a file-like object::

  fp = io.BytesIO(...)  # readable file-like object
  reader = jsonlines.Reader(fp)
  first = reader.read()
  second = reader.read()
  reader.close()
  fp.close()

While the :py:meth:`Reader.read` method can be used directly, it is
often more convenient to use iteration::

  for obj in reader:
      ...

Custom iteration flags, such as type checks, can be specified by
calling :py:meth:`Reader.iter()` instead::

  for obj in reader.iter(type=dict, skip_invalid=True):
      ...


A :py:class:`Writer` also wraps a file-like object, and can
write both a single object, or multiple objects at once::

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
case they will be closed automatically. Note that this does not close
the passed-in file-like object since that object‘s life span is
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


This should be enough to get you started. See the API docs below for
more details.


API
===

Convenience
-----------

.. autofunction:: jsonlines.open

Reader
------

.. autoclass:: jsonlines.Reader
   :members:

Writer
------

.. autoclass:: jsonlines.Writer
   :members:

Errors
------

.. autoclass:: jsonlines.Error
   :members:

.. autoclass:: jsonlines.InvalidLineError
   :members:


Contributing
============

The source code and issue tracker for this package can be found on Github:

  https://github.com/wbolster/jsonlines


Version history
===============

* 1.x.x

  *not yet released*

  * minimum python versions are python 3.4+ and python2.7+
  * implemented lots of configuration options
  * add proper exceptions handling
  * add proper documentation
  * switch to semver


* 0.0.1

  Released at 2015-03-02.

  * initial release with basic functionality


License
=======

Copyright © 2016, Wouter Bolsterlee

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice, this
  list of conditions and the following disclaimer in the documentation and/or
  other materials provided with the distribution.

* Neither the name of the author nor the names of the contributors may be used
  to endorse or promote products derived from this software without specific
  prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

*(This is the OSI approved 3-clause "New BSD License".)*
