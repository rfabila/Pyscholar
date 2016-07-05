.. _installation:

============
Installation
============

Requirements
================
Pyscholar required to have the following packages installed:

* `Python <https://www.python.org/download/releases/2.7/>`_ >=2.7
* `Networkx <http://networkx.github.io/documentation/networkx-1.7/install.html>`_
* `Matplotlib <http://matplotlib.org/users/installing.html>`_

.. note:: Pyscholar does not support Python 3.x

Step-by-Step Installation Guide
================================
Before installing Pyscholar you must get your API Key in the following `link <http://dev.elsevier.com/myapikey.html>`_.

Once you have the API key. We continue with the installation of Pyscholar.

1. Clone the repository first as follows:

.. code-block:: console

   $ git clone https://github.com/rfabila/Pyscholar.git

2. Then you must run setup.py and enter your API KEY


.. code-block:: console

   $ python setup.py
   $ Your scopus api key:(Here you enter your API Key)

3.  Finally we will check the installation for this first navigate to the installation directory then execute python and finally we import the package Pyscholar:


.. code-block:: console

   $ cd ~/Pyscholar/src
   $ python
   Python 2.7.6 (default, Jun 22 2015, 17:58:13) 
   [GCC 4.8.2] on linux2
   Type "help", "copyright", "credits" or "license" for more information.
   >>> 

.. code-block:: python

   >>> import pyscholar

If the import of pyscholar not failed then the installation was successful. 