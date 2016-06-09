from setuptools import setup, find_packages
import ConfigParser
import sys
import os

if "install" in sys.argv:
    #We create keys.cfg before installing
    keysParser = ConfigParser.ConfigParser()
    keysParser.add_section("Keys")
    keysParser.set('Keys', 'Scopus', "")
    dirPath = os.path.dirname(os.path.abspath(__file__))
    originalMask = os.umask(0)
    keysDescriptor = os.open(os.path.join(dirPath, 'pyscholar/keys.cfg'), os.O_WRONLY | os.O_CREAT, 0666)
    keysFile = os.fdopen(keysDescriptor, 'w')
    os.umask(originalMask)
    keysParser.write(keysFile)
    keysFile.close()

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='pyscholar',
      version='1.0.0.dev1',
      description='A python library to access Scopus',
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