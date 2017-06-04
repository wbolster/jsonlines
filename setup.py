import os
from setuptools import setup


with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as fp:
    long_description = fp.read()

setup(
    name="jsonlines",
    version="1.1.1",
    description="Library with helpers for the jsonlines file format",
    long_description=long_description,
    author="Wouter Bolsterlee",
    author_email="wouter@bolsterl.ee",
    url="https://github.com/wbolster/jsonlines",
    packages=['jsonlines'],
    install_requires=['six'],
    license='BSD',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: Log Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Logging',
        'Topic :: Utilities',
    ],
)
