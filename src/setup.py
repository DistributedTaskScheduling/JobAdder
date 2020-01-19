#!/usr/bin/env python3

import unittest

from setuptools import find_packages, setup


def discover_ja_tests():
    _tl = unittest.TestLoader()
    _ts = _tl.discover('test', '*.py')
    return _ts


setup(
    name='jobadder',
    version="0.0.1",
    description='JobAdder: a package for priority-based scheduling of Docker jobs to mwork machines',
    long_description='',
    author='Johannes Gäßler, ',  # TODO add everyone else
    author_email='johannesg@5d6.de, ',  # TODO add everyone else
    url='https://github.com/DistributedTaskScheduling/JobAdder',
    packages=find_packages(),
    package_data={},
    scripts=[],
    test_suite='setup.discover_ja_tests',
    keywords=[],
    license='GPL3',
    install_requires=[],
    classifiers=[],
)
