#!/usr/bin/env python

# Copyright (C) 2012 Bob Bowles <bobjohnbowles@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the MIT License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# You should have received a copy of the MIT License
# along with this program.



try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os


# TODO: locale root. ATM there is no locale info in the project.
#targetLocaleRoot = ''
## TODO Windows stuff needs fixing
#if os.name == 'nt': targetLocaleRoot = os.path.join('C:', 'Python32')
#elif os.name == 'posix': targetLocaleRoot = os.path.join('/', 'usr', 'share')


# sort out the data files for the app
dataFiles = []


# sort out package data (e.g. gifs etc used in the app)
fileList = []
packageDir = '.'
packageRoot = os.path.join(packageDir, 'diary')


# get a reference to the version number from the package being built
import sys
sys.path.insert(0, packageDir)
from diary import __version__


# this template is for non-python files. we don't need it atm because this
# is done in MANIFEST.in via recursive-include
#imageRoot = 'images'
#for file in os.listdir(os.path.join(packageRoot, imageRoot)):
#    fileList.append(os.path.join(imageRoot, file))
#fileList.sort()


packageData = {'diary': fileList}


# now run setup
setup(
    name='django-diary',
    version=__version__,
    description='A pluggable diary app for use in the Django framework.',
    long_description=open('README.rst').read(),
    author='Bob Bowles',
    author_email='bobjohnbowles@gmail.com',
    url='http://pypi.python.org/pypi/diary/',
    license='MIT License',
    keywords=["Diary", "Django",],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Django :: 1.8",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",  # TODO: only tested on Linux
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary",
        "Topic :: Utilities",
    ],
    package_dir={'': packageDir},
    packages=['diary', 'diary.migrations'],
    install_requires=[
        'Django>=1.8.3',
        'django-datetime-widget>=0.9.3',
        'django-model-utils>=2.3.1',
        'pytz>=2015.4',
        'six>=1.9.0',
    ],
    package_data=packageData,
    data_files=dataFiles,
)



