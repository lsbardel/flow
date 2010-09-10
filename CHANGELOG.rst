
jFlow 0.4.a2
===========================
 * Added the ``libs`` directory containing external libraries which are not regularly updated.
 * External libraries are added to the ``PYTHONPATH``, if needed, when importing ``jflow``.
 * Portfolio views are managed by python-stdnet__ ORM.


jFlow 0.4.a1 - (2010 July 17)
================================
 * Added to PyPI
 * Refactored `instdata` and `trade` models. Not backward compatible
 * Created django-piston API
 * Added `jfsite` application site with several `djpcms` plugins


jFlow 0.3 -  (2010 March 15)
================================
 * First tagged release.
 * Added small management utility for cleaning stale instruments (python manage.py cleaninst)
 * Added TabularInline BondIssuer in BondClass admin


__ http://packages.python.org/python-stdnet/