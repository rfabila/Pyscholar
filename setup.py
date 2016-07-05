from setuptools import setup, find_packages
import ConfigParser
import sys
import os

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='pyscholar',
      version='1.0.0.dev3',
      description='A python library to access academic APIs',
      url='http://rfabila.github.io/Pyscholar/',
      author='DesarrolloDeSoftware',
      author_email='rfabila@math.cinvestav.edu.mx',
      license='GNU',
      packages=find_packages(),
      install_requires=[
          'networkx',
          'matplotlib',
          'pandas'
      ],
      include_package_data=True,
      zip_safe=False)