ai-aside
#############################

|pypi-badge| |ci-badge| |codecov-badge| |doc-badge| |pyversions-badge|
|license-badge| |status-badge|

Purpose
*******

This plugin holds LLM related blocks and tools, initially the summary XBlock aside but eventually more options.

Getting Started
***************

Developing
==========

One Time Setup
--------------
.. code-block::

  # Clone the repository
  git clone git@github.com:openedx/ai-aside.git
  cd ai-aside

  # Set up a virtualenv using virtualenvwrapper with the same name as the repo and activate it
  mkvirtualenv -p python3.8 ai-aside

Local testing
~~~~~~~~~~~~~
To test your changes locally, you will need to install the package from your local branch into edx-platform. For example, if using devstack, copy or clone your branch into <devstack-parent>/src/ai-aside. Then, in an lms or cms shell, run ``pip install -e /edx/src/ai-aside``.  The plug-in configuration will automatically be picked up once installed, and changes will be hot reloaded.

Enabling the Aside
~~~~~~~~~~~~~~~~~~

For the summary aside to work, you will have to make two changes in the LMS admin:

1. You must create an ``XBlockAsidesConfig`` (admin URL: `/admin/lms_xblock/xblockasidesconfig/`). This model has a list of blocks you do not want asides to apply to that can be left alone, and an enabled setting that unsurprisingly should be True.

2. You must enable a course waffle flag for each course you want to summarize. ``summaryhook.summaryhook_enabled`` is the main one, ``summaryhook_enabled.summaryhook_staff_only`` can be used if you only want staff to see it.

Every time you develop something in this repo
---------------------------------------------
.. code-block::

  # Activate the virtualenv
  workon ai-aside

  # Grab the latest code
  git checkout main
  git pull

  # Install/update the dev requirements
  make requirements

  # Run the tests and quality checks (to verify the status before you make any changes)
  make validate

  # Make a new branch for your changes
  git checkout -b <your_github_username>/<short_description>

  # Using your favorite editor, edit the code to make your change.
  vim ...

  # Run your new tests
  pytest ./path/to/new/tests

  # Run all the tests and quality checks
  make validate

  # Commit all your changes
  git commit ...
  git push

  # Open a PR and ask for review.

Deploying
=========

This plugin is deployed on edx.org via EDXAPP_EXTRA_REQUIREMENTS.

License
*******

The code in this repository is licensed under the AGPL 3.0 unless
otherwise noted.

Please see `LICENSE.txt <LICENSE.txt>`_ for details.

Contributing
************

Contributions are very welcome.
Please read `How To Contribute <https://openedx.org/r/how-to-contribute>`_ for details.

This project is currently accepting all types of contributions, bug fixes,
security fixes, maintenance work, or new features.  However, please make sure
to have a discussion about your new feature idea with the maintainers prior to
beginning development to maximize the chances of your change being accepted.
You can start a conversation by creating a new issue on this repo summarizing
your idea.

The Open edX Code of Conduct
****************************

All community members are expected to follow the `Open edX Code of Conduct`_.

.. _Open edX Code of Conduct: https://openedx.org/code-of-conduct/

People
******

The assigned maintainers for this component and other project details may be
found in `Backstage`_. Backstage pulls this data from the ``catalog-info.yaml``
file in this repo.

.. _Backstage: https://open-edx-backstage.herokuapp.com/catalog/default/component/ai-aside

Reporting Security Issues
*************************

Please do not report security issues in public. Please email security@tcril.org.

.. |pypi-badge| image:: https://img.shields.io/pypi/v/ai-aside.svg
    :target: https://pypi.python.org/pypi/ai-aside/
    :alt: PyPI

.. |ci-badge| image:: https://github.com/openedx/ai-aside/workflows/Python%20CI/badge.svg?branch=main
    :target: https://github.com/openedx/ai-aside/actions
    :alt: CI

.. |codecov-badge| image:: https://codecov.io/github/openedx/ai-aside/coverage.svg?branch=main
    :target: https://codecov.io/github/openedx/ai-aside?branch=main
    :alt: Codecov

.. |doc-badge| image:: https://readthedocs.org/projects/ai-aside/badge/?version=latest
    :target: https://docs.openedx.org/projects/ai-aside
    :alt: Documentation

.. |pyversions-badge| image:: https://img.shields.io/pypi/pyversions/ai-aside.svg
    :target: https://pypi.python.org/pypi/ai-aside/
    :alt: Supported Python versions

.. |license-badge| image:: https://img.shields.io/github/license/openedx/ai-aside.svg
    :target: https://github.com/openedx/ai-aside/blob/main/LICENSE.txt
    :alt: License

.. TODO: Choose one of the statuses below and remove the other status-badge lines.
.. |status-badge| image:: https://img.shields.io/badge/Status-Experimental-yellow
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Maintained-brightgreen
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Deprecated-orange
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Unsupported-red
