==========
codeowners
==========


.. image:: https://img.shields.io/pypi/v/codeowners.svg
        :target: https://pypi.python.org/pypi/codeowners

.. image:: https://img.shields.io/travis/nmusolino/codeowners.svg
        :target: https://travis-ci.org/nmusolino/codeowners

.. image:: https://readthedocs.org/projects/codeowners/badge/?version=latest
        :target: https://codeowners.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


Utility for identifying the owners of files under Github's CODEOWNERS feature.

Github repository users can designate *`code owners`_* for files within their repos.  Code owners
are automatically added as reviewers of pull requests, and, optionally, their approval is required to
merge pull requests for designated branches.

.. _`code owners`: https://blog.github.com/2017-07-06-introducing-code-owners/

As detailed in `Github's documentation`, CODEOWNERS files are very similar to .gitignore files.

.. _`Github's documentation`:  https://help.github.com/articles/about-codeowners/

The ``codeowners`` utility is intended to help developers working with this feature::

  $ codeowners src/mylib.h src/main.c
  src/mylib.h:  @psmith @rgonzalez
  src/main.c:  @psmith @njohnson

Features
--------
List owners of each file in a repository::

  $ codeowners notes.txt src/ tests/
  notes.txt:  @agreen
  src/mylib.h:  @psmith @rgonzalez

Identify the specific pattern in the CODEOWNERS file that designates owners::

  $ codeowners --verbose src/mylib.h
  .github/CODEOWNERS:37: src/**.h: src/mylib.h: @psmith @rgonzalez

Identify all the owners of files modified by git commits::

  $ codeowners --commits c0f5855954ce47f93cce353d4d9b9a9e2a92b9a5
  [...]
  $ codeowners --commits my_feature_branch
  [...]


License
-------

This is free software.  It is made available under the GNU General Public License v3.

Credits
-------

This package was created with Cookiecutter_ and the `elgertam/cookiecutter-pipenv`_ project template, based on `audreyr/cookiecutter-pypackage`_.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`elgertam/cookiecutter-pipenv`: https://github.com/elgertam/cookiecutter-pipenv
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
