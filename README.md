# Pyscholar
![pyversion](https://img.shields.io/badge/python-2.7-brightgreen.svg)
![license](https://img.shields.io/badge/license-GNU-blue.svg)
-----------
A library to create collaboration science networks.
### Prerequisites
-------------
- Python >= 2.7
- IPython >=1.2.1

### Installation
-----------
Before installing Pyscholar you must get your API Key in the following [link][df1].

First you need to clone the repository:
```sh
$ git clone https://github.com/rfabila/Pyscholar.git
```
Then you must run setup.py and enter your API KEY
```sh
$ python setup.py
$ Your scopus api key:(Here you enter your API Key)
```
### Basic Usage
-----------
First navigate to the next directory: 
```sh
$ cd ~/Pyscholar/src
```
Then execute IPython
```sh
$ ipython
Python 2.7.6 (default, Jun 22 2015, 17:58:13) 
Type "copyright", "credits" or "license" for more information.

IPython 1.2.1 -- An enhanced Interactive Python.
?         -> Introduction and overview of IPython's features.
%quickref -> Quick reference.
help      -> Python's own help system.
object?   -> Details about 'object', use 'object??' for extra details.
```
Finally import the pyscholar package 
```
In [1]: import pyscholar
```
And now you can do some searching.

For example, the following is an search by author that receives the name and lastname and the function will return a list of IDs associated with the author.
```
In [2]: pyscholar.find_author_scopus_id_by_name("Ruy", "Fabila-Monroy")
Out[2]: [u'56013555800', u'16635924700']
```
### License
-----------
This project is licensed under the GNU GENERAL PUBLIC LICENSE - see the [LICENSE][df2] file for details

[df1]: <http://dev.elsevier.com/myapikey.html>
[df2]: <https://github.com/rfabila/Pyscholar/blob/master/LICENSE>