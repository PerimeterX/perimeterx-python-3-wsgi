#!/usr/bin/env python

from setuptools import setup, find_packages

version = 'v1.1.0'
setup(name='perimeterx-python-3-wsgi',
      version=version,
      license='MIT',
      description='PerimeterX Python 3 WSGI middleware',
      author='Johnny Tordgeman',
      author_email='johnny@perimeterx.com',
      url='https://github.com/PerimeterX/perimeterx-python-3-wsgi',
      download_url='https://github.com/PerimeterX/perimeterx-python-3-wsgi/tarball/' + version,
      packages=find_packages(exclude=['dev', 'test*']),
      package_data={'perimeterx': ['templates/*']},
      install_requires=['pystache>=0.5.4', 'requests>=2.22.0', 'setuptools==41.4.0', 'Werkzeug==0.16.0', 'pycryptodome>=3.9.0'],
      classifiers=['Intended Audience :: Developers',
                   'Programming Language :: Python :: 3.7'])
