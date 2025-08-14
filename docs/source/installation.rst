Installation
============

Requirements
------------

* Python 3.11 or higher
* pip or Poetry package manager
* networkx for Graph data structures.
* plotly for Knit Graph visualization

Install from PyPI
-----------------

The easiest way to install the package is from PyPI:

.. code-block:: bash

   pip install knit-graphs

Or using Poetry:

.. code-block:: bash

   poetry add knit-graphs

Install from Source
-------------------

To install the latest development version from source:

.. code-block:: bash

   git clone https://github.com/mhofmann-Khoury/knit-graphs.git
   cd your-repo
   pip install -e .

Or with Poetry:

.. code-block:: bash

   git clone https://github.com/mhofmann-Khoury/knit-graphs.git
   cd your-repo
   poetry install

Development Installation
------------------------

For development and contributing:

.. code-block:: bash

   git clone https://github.com/mhofmann-Khoury/knit-graphs.git
   cd your-repo
   poetry install --with dev,docs

This installs the package with all development dependencies including testing and documentation tools.

Verify Installation
-------------------

To verify the installation worked correctly:

.. code-block:: python

   import knit-graphs
   print(knit-graphs.__version__)
