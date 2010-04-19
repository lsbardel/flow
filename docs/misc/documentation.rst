.. _misc-documentation:

How the jFlow documentation works
==================================

\... and how to contribute.

jFlow documentation uses the Sphinx__ documentation system, which in turn is
based on docutils__. The basic idea is that lightly-formatted plain-text
documentation is transformed into HTML, PDF, and any other output format.

__ http://sphinx.pocoo.org/
__ http://docutils.sf.net/

To actually build the documentation locally, you'll currently need to install
Sphinx -- ``pip install sphinx`` should do the trick.

Then, building the html is easy; just ``make html`` from the ``docs`` directory.

To get started contributing, you'll want to read the `ReStructuredText
Primer`__. After that, you'll want to read about the `Sphinx-specific markup`__
that's used to manage metadata, indexing, and cross-references.

__ http://sphinx.pocoo.org/rest.html
__ http://sphinx.pocoo.org/markup/
