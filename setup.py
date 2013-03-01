# -*- coding: utf-8 -*-
"""Installer for this package."""

from setuptools import setup
from setuptools import find_packages

import os

# shamlessly stolen from Hexagon IT guys
def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.1dev'

setup(name='pipaalarm',
      version=version,
      description="Send sms when specified devices get out of range.",
      long_description=read('README.rst') +
                       read('LICENSE.txt'),
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='web.py Python',
      author='Jaka Hudoklin',
      author_email='jakahudoklin@gmail.com',
      url='http://www.github.com/offlinehacker/pipaalarm',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True,
      zip_safe=False,
      dependency_links =
            ["https://github.com/offlinehacker/scapy/tarball/master#egg=scapy-2.1.1-dev",
             "https://github.com/offlinehacker/pysms/tarball/master#egg=pysms-0.2-dev"],
      install_requires=[
          'six',
          'setuptools',
          'configparser', # Config file parsing
          'gevent', # Event loop routine
          'web.py', # Web server
          'scapy', # Arping
          'pysms'
      ],
      tests_require = [
          "mock"
      ],
      entry_points="""
          [console_scripts]
          pipaalarm = pipaalarm.pipaalarm:main""",
      test_suite="pipaalarm.tests",
      )
