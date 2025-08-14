Installation
============

.. TODO: Update installation instructions for your project

Requirements
------------

.. TODO: List system requirements and Python version

* Python 3.11 or higher
* pip or Poetry package manager

Install from PyPI
-----------------

The easiest way to install the package is from PyPI:

.. code-block:: bash

   pip install your-project-name

Or using Poetry:

.. code-block:: bash

   poetry add your-project-name

Install from Source
-------------------

To install the latest development version from source:

.. code-block:: bash

   git clone https://github.com/your-username/your-repo.git
   cd your-repo
   pip install -e .

Or with Poetry:

.. code-block:: bash

   git clone https://github.com/your-username/your-repo.git
   cd your-repo
   poetry install

Development Installation
------------------------

For development and contributing:

.. code-block:: bash

   git clone https://github.com/your-username/your-repo.git
   cd your-repo
   poetry install --with dev,docs

This installs the package with all development dependencies including testing and documentation tools.

Verify Installation
-------------------

To verify the installation worked correctly:

.. code-block:: python

   import your_project_name
   print(your_project_name.__version__)
