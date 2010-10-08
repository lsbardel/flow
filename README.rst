
.. rubric:: Portfolio analysis and risk management financial library.

--

:Documentation: http://packages.python.org/jflow/
:Dowloads: http://pypi.python.org/pypi/jflow/
:Source: http://github.com/lsbardel/jflow
:Keywords: finance, quantitative, timeseries, data, analysis, django, python

--

Python package for portfolio analysis.


.. _jflow-requirements:

Requirements
======================

 * Django_ for database and web-framework.
 * ccy_ for currency and date manipulation.
 * stdnet_ for fast in-memory and persistent data-structures using redis_.
 * dynts_ for timeseries analysis.
 * unuk_ for creating ``rpc`` servers.
 * django-extracontent_ a django utility application.


Running Tests
==================

To use ``jflow`` you need to install redis_, which is the only database back-end supported by stdnet_.
If you are working in linux, simply download the latest redis version and compile it.
If you are working on windows you can get binaries here__.
Make sure the version you are  installing is greater than 2.0.

__ http://code.google.com/p/servicestack/wiki/RedisWindowsDownload

Start redis_ and open a separate shell. You can run tests from the console from within the
``jflow`` source directory::

	python runtests.py
 

Application Example
========================

In the ``example`` directory you can find an application of the library.
    
Good luck

.. _Django: http://www.djangoproject.com/
.. _ccy: http://code.google.com/p/ccy/
.. _stdnet: http://packages.python.org/python-stdnet/
.. _dynts: http://code.google.com/p/dynts/
.. _unuk: http://packages.python.org/unuk/
.. _django-extracontent: http://pypi.python.org/pypi/django-extracontent/
.. _redis: http://code.google.com/p/redis/




