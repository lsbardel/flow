
:Documentation: http://packages.python.org/jflow/
:Dowloads: http://pypi.python.org/pypi/jflow/
:Source: http://github.com/lsbardel/jflow
:Keywords: finance, quantitative, timeseries, data, analysis, django, python

--

Python package for quantitative finance and econometric analysis


Requirements
======================

 * django__
 * ccy__
 * stdnet__
 * dynts__


Running Tests
==================

To use jflow you need to install redis__, which is the only database back-end supported by stdnet__.
If you are working in linux, simply download the latest redis version and compile it. If you are working on windows
you can get binaries here__. Make sure the version you are  installing is greater than 2.0.

Start redis and open a separate shell. You can run tests from the console from within the ``jflow`` source directory::

	python runtests.py
	
or, once installed the package, from the interactive console::

    import jflow
    jflow.runtests()    
    
Good luck

__ http://www.djangoproject.com/
__ http://code.google.com/p/ccy/
__ http://packages.python.org/python-stdnet/
__ http://code.google.com/p/dynts/
__ http://code.google.com/p/redis/
__ http://packages.python.org/python-stdnet/
__ http://code.google.com/p/servicestack/wiki/RedisWindowsDownload




