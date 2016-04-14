# Pyscholar
-----------
![pyversion](https://img.shields.io/badge/python-2.7-brightgreen.svg) ![license](https://img.shields.io/badge/license-GNU-blue.svg)
-----------
A library to create collaboration science networks.
### Prerequisites
-------------
- Python >= 2.7

**Pyscholar does not support Python 3.x**
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
First navigate to the instalation directory: 
```sh
$ cd ~/Pyscholar/src
```
Then execute python
```python
$ python
Python 2.7.6 (default, Jun 22 2015, 17:58:13) 
[GCC 4.8.2] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> 
```
And import the pyscholar package 
```python
>>> import pyscholar
```
And now you can do some searching.

For example, the following function performs a search by author. It receives the first and last name, and returns a list of IDs associated with the author.
```python
>>> pyscholar.find_author_scopus_id_by_name("Ruy", "Fabila-Monroy")
>>> [u'56013555800', u'16635924700']
```
### License
-----------
This project is licensed under the GNU GENERAL PUBLIC LICENSE - see the [LICENSE][df2] file for details

[df1]: <http://dev.elsevier.com/myapikey.html>
[df2]: <https://github.com/rfabila/Pyscholar/blob/master/LICENSE>