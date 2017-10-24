=========
Pyscholar
=========

|pyversion| |license|
---------------------

A library to create science collaboration networks.

Requirements
------------

- `Python <https://www.python.org/download/releases/2.7/>`_  ≥ 2.7
- `Networkx <http://networkx.github.io/documentation/networkx-1.7/install.html>`_
- `Matplotlib <http://matplotlib.org/users/installing.html>`_

**Pyscholar does not support Python 3.x**

Installation
------------

Before installing Pyscholar you must get your API Key in the following
`link <http://dev.elsevier.com/myapikey.html>`__.

First you need to clone the repository:

.. code-block:: sh

    $ git clone https://github.com/rfabila/Pyscholar.git

Then you must run setup.py and enter your API KEY

.. code-block:: sh

    $ python setup.py
    $ Your Scopus API key:(Enter here your API Key)

Basic Usage
-----------

First navigate to the installation directory:

.. code:: sh

    $ cd ~/Pyscholar/src

Then execute python

.. code:: sh

    $ python
    Python 2.7.6 (default, Jun 22 2015, 17:58:13) 
    [GCC 4.8.2] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>> 

And import the Pyscholar package in the REPL

.. code:: python

    >>> import pyscholar

And now you can do some searching.

Examples
--------

The following function performs a search by author.
It receives the first and last name, and returns a list of IDs associated
with the author.

.. code:: python

    >>> pyscholar.find_author_scopus_id_by_name("Ruy", "Fabila-Monroy")
    >>> [u'56013555800', u'16635924700']

License
-------

This project is licensed under the GNU General Public License v2.0 - see the
`LICENSE <https://github.com/rfabila/Pyscholar/blob/master/LICENSE>`__
file for details.

.. |pyversion| image:: https://img.shields.io/badge/python-2.7-brightgreen.svg
.. |license| image:: https://img.shields.io/badge/license-GNU-blue.svg
