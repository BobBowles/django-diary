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
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup

import os


# TODO: locale root. ATM there is no locale info in the project.
#targetLocaleRoot = ''
## TODO Windows stuff needs fixing
#if os.name == 'nt': targetLocaleRoot = os.path.join('C:', 'Python32')
#elif os.name == 'posix': targetLocaleRoot = os.path.join('/', 'usr', 'share')


# sort out the data files for the app
dataFiles = []


# sort out package data (e.g. gifs etc used in the app)
packageFiles = []
packageDir = '.'
packageRoot = os.path.join(packageDir, 'diary')


# get a reference to the version number from the package being built
import sys
sys.path.insert(0, packageDir)
from diary import __version__


def collectPackageData(packageRoot, subdirectory):
    """
    Helper to recursively collect up the package data files.
    """
    root = os.getcwd()
    os.chdir(packageRoot)
    for dirpath, dirnames, filenames in os.walk(subdirectory):
        for filename in filenames:
            packageFiles.append(os.path.join(dirpath, filename))
    os.chdir(root)


# gather up the non-python package files
collectPackageData(packageRoot, 'static')
collectPackageData(packageRoot, 'templates')
packageFiles.sort()
packageData = {'diary': packageFiles}


# now run setup
setup(
    name='django-diary',
    version=__version__,
    description='A pluggable diary app for use in the Django framework.',
    long_description_content_type="text/x-rst",
    long_description=open('README.rst').read(),
    author='Bob Bowles',
    author_email='bobjohnbowles@gmail.com',
    url='http://pypi.python.org/pypi/django-diary/',
    license='MIT License',
    keywords=["Diary", "Django",],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Django :: 4.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",  # TODO: only tested on Linux
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary",
        "Topic :: Utilities",
    ],
    package_dir={'': packageDir},
    packages=[
        'diary',
        'diary.formats',
        'diary.formats.en',
        'diary.migrations',
        'diary.management',
        'diary.management.commands',
        'diary.templatetags',
    ],
    install_requires=[
        'Django>=4.2.5, <5',
        'django-datetime-widget2>=0.9.5',
        'DateTime>=5.2',
    ],
    package_data=packageData,
    data_files=dataFiles,
    zip_safe=False,
)
