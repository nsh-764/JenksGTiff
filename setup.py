# -*- coding: utf-8 -*-
"""
Created on Sat May 12 03:28:51 2018

@author: nikhil.s.hubballi
"""

from setuptools import setup
from os import path
from ast import parse
try:
    from future_builtins import filter
except ImportError:
    pass



with open(path.join('jenksGTiff', '__init__.py')) as f:
    __version__ = parse(next(filter(lambda line: line.startswith('__version__'),f))).body[0].value.s


setup(name='jenksGTiff',
      version=__version__,
      description='Apply Jenks Natural Breaks on Geotiff files and outputs image with graduated symbology',
      url='https://github.com/nsh-764/PyJenks',
      author='Nikhil S Hubballi',
      author_email='nikhil.hubballi@gmail.com',
      license='MIT',
      packages=['jenksGTiff'],
      include_package_data=True,
      classifiers=[
        "Programming Language :: Python",
        "Development Status :: 1 - Beta",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Scientific/Engineering",
        ],
      zip_safe=False)
