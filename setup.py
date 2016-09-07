import os
from setuptools import setup

import jsonlines

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as fp:
    long_description = fp.read()

setup(
    name="jsonlines",
    version=jsonlines.__version__,
    description="Library with helpers for the jsonlines file format",
    long_description=long_description,
    author="Wouter Bolsterlee",
    author_email="uws@xs4all.nl",
    url="https://github.com/wbolster/jsonlines",
    packages=['jsonlines'],
    install_requires=['six'],
    license='BSD',
    classifiers=[],  # TODO
)
