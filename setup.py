from setuptools import setup
import ConfigParser

keys = ConfigParser.ConfigParser()
keys.read("keys.cfg")

ans = raw_input("Do you want to set your Scopus key now? (Y/N) ")
if ans.lower() == 'y':
    key = raw_input("Your scopus api key: ")
    keys.set('Keys', 'Scopus', key)
    cfgfile = open("keys.cfg", 'w')
    keys.write(cfgfile)

setup(name='Pyscholar',
      version='0.1',
      description='A python library to access Scopus',
      url='http://rfabila.github.io/Pyscholar/',
      author='DesarrolloDeSoftware',
      author_email='rfabila@math.cinvestav.mx',
      license='GNU',
      packages=['pyscholar'],
      install_requires=[
          'networkx',
          'matplotlib',
          'pandas'
      ],
      zip_safe=False)