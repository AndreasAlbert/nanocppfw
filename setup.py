"""pypi package setup."""
from __future__ import print_function
import codecs
from os import path
from setuptools import setup, find_packages
try:
    import ROOT  # pylint: disable=W0611
except ImportError:
    print("ROOT is required by this library.")

DEPS = ["law", "pybind11"]

HERE = path.abspath(path.dirname(__file__))

with codecs.open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name='nanocppfw',
    version='0.0.1',
    description='',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://github.com/AndreasAlbert/nanocppfw',
    author='Andreas Albert',
    author_email='andreas.albert@cern.ch',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
    keywords='NanoAOD',
    packages=find_packages(),
    zip_safe=False,
    install_requires=DEPS,
    # setup_requires=['pytest-runner', 'pytest-cov'],
    # tests_require=['pytest'],
    project_urls={
        'Source': 'https://github.com/AndreasAlbert/nanocppfw',
    }, )
