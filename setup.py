#!/usr/bin/env python
'''Based on an idea of stackexchange user A Feldman
https://tex.stackexchange.com/questions/173317/is-there-a-latex-wrapper-for-use-in-google-docs'''
from setuptools import setup, find_packages
import os


def find_scripts():
    scripts = ['bin/glatex']
    return scripts


setup(
    name='glatex',
    version='0.21',
    install_requires=[],
    packages=find_packages(),
    include_package_data=True,
    scripts=find_scripts(),
    author='Michael Reimann',
    author_email='michael.reimann@epfl.ch',
    description='Compile latex code contained in google docs',
    license='Restricted',
    keywords=('latex',
              'GDocs'),
    url='http://bluebrain.epfl.ch',
    classifiers=['Development Status :: 3 - Alpha',
                 'Environment :: Console',
                 'License :: Proprietary',
                 'Operating System :: POSIX',
                 'Topic :: Utilities',
                 ],
)
