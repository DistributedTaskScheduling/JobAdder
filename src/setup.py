#!/usr/bin/env python3

from setuptools import find_packages, setup


setup(
    name='jobadder',
    version="0.0.1",
    description='JobAdder: a package for priority-based scheduling of Docker jobs to work machines',
    long_description='',
    author='Ilia Bozhinov, Johannes Gäßler, ',  # TODO add everyone else
    author_email='ammen99@gmail.com, johannesg@5d6.de, ',  # TODO add everyone else
    url='https://github.com/DistributedTaskScheduling/JobAdder',
    packages=find_packages(exclude=["test", "test.*", "ja_integration", "ja_integration.*"]),
    package_data={},
    keywords=[],
    license='GPL3',
    install_requires=[],
    classifiers=[],
)
