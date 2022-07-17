========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |github-actions| |requires|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/covariates-in-neuroimaging/badge/?style=flat
    :target: https://covariates-in-neuroimaging.readthedocs.io/
    :alt: Documentation Status

.. |github-actions| image:: https://github.com/GalBenZvi/covariates-in-neuroimaging/actions/workflows/github-actions.yml/badge.svg
    :alt: GitHub Actions Build Status
    :target: https://github.com/GalBenZvi/covariates-in-neuroimaging/actions

.. |requires| image:: https://requires.io/github/GalBenZvi/covariates-in-neuroimaging/requirements.svg?branch=main
    :alt: Requirements Status
    :target: https://requires.io/github/GalBenZvi/covariates-in-neuroimaging/requirements/?branch=main

.. |codecov| image:: https://codecov.io/gh/GalBenZvi/covariates-in-neuroimaging/branch/main/graphs/badge.svg?branch=main
    :alt: Coverage Status
    :target: https://codecov.io/github/GalBenZvi/covariates-in-neuroimaging

.. |version| image:: https://img.shields.io/pypi/v/neurocov.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/neurocov

.. |wheel| image:: https://img.shields.io/pypi/wheel/neurocov.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/neurocov

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/neurocov.svg
    :alt: Supported versions
    :target: https://pypi.org/project/neurocov

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/neurocov.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/neurocov

.. |commits-since| image:: https://img.shields.io/github/commits-since/GalBenZvi/covariates-in-neuroimaging/v0.0.0.svg
    :alt: Commits since latest release
    :target: https://github.com/GalBenZvi/covariates-in-neuroimaging/compare/v0.0.0...main



.. end-badges

A package describing different covariates in Neuroimaging studies

* Free software: Apache Software License 2.0

Installation
============

::

    pip install neurocov

You can also install the in-development version with::

    pip install https://github.com/GalBenZvi/covariates-in-neuroimaging/archive/main.zip


Documentation
=============


https://covariates-in-neuroimaging.readthedocs.io/


Development
===========

To run all the tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
