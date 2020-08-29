"""Setup module for beacontools."""

from setuptools import setup, find_packages
from codecs import open
from os import path
import sys

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='beacontools',

    version='2.0.2',

    description='A Python library for working with various types of Bluetooth LE Beacons.',
    long_description=long_description,

    url='https://github.com/citruz/beacontools',

    author='Felix Seele',
    author_email='fseele@gmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    keywords='beacons ibeacon eddystone bluetooth low energy ble',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'construct>=2.9.52,<2.11',
        'ahocorapy==1.6.1'
    ],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'scan': ['PyBluez==0.22'] if sys.platform.startswith("linux") else [],
        'dev': ['check-manifest'],
        'test': [
            'coveralls~=2.1',
            'pytest~=6.0',
            'pytest-cov~=2.10',
            'mock~=4.0',
            'check-manifest==0.42',
            'pylint',
            'readme_renderer',
            'docutils'
        ],
    },
)
