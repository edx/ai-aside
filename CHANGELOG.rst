Change Log
##########

..
   All enhancements and patches to ai_aside will be documented
   in this file.  It adheres to the structure of https://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).

   This project adheres to Semantic Versioning (https://semver.org/).

.. There should always be an "Unreleased" section for changes pending release.

Unreleased
**********

3.8.10 - 2026-09-28
**********************************************
* Added Python 3.12 support, per the org-wide Python 3.12 upgrade process (libraries keep
  both 3.11 and 3.12): tox/CI now run the full ``py{311,312}-django{42,52}`` matrix, the
  weekly requirements-upgrade workflow now compiles with Python 3.12, and ``setup.py``
  declares ``python_requires = >=3.11`` with 3.11/3.12 classifiers.
* Regenerated ``requirements/*.txt`` from scratch with Python 3.12 (``make upgrade``).
  Two pins had to be held back in ``requirements/constraints.txt`` to keep Python 3.11 and
  Django 4.2 support: ``code-annotations<3.0.0`` (3.0.0 requires Python >=3.12) and
  ``djangorestframework<3.18.0`` (3.18.0 requires Django >=5.2). XBlock is held to
  ``xblock<6.0.0`` for the same reason (6.0.0 requires Python >=3.12) -- this is the
  biggest of the three since XBlock is ai-aside's core runtime dependency, so it's called
  out separately for visibility.
* Fixed the ``quality``, ``docs``, and ``pii_check`` tox environments, which were broken
  independently of the Python version bump: pinned ``setuptools<81`` in each (newer
  setuptools dropped ``pkg_resources``, needed by ``edx_lint``'s pylint plugin and by
  XBlock); added a ``basepython`` for each since ``[testenv]``'s ``basepython`` is now
  Python-version-conditional; recompiled ``requirements/quality.txt`` to resolve an
  incompatible ``edx-lint``/``astroid`` pin combination; disabled the new pylint
  ``too-many-positional-arguments`` check alongside the already-disabled
  ``too-many-arguments``; mocked the edx-platform-only ``openedx``/``lms`` imports for
  Sphinx autodoc; and added the missing toctree entry for ``docs/how-tos/monitoring.rst``.
* Dropped the last remaining Python 3.8 references: ``.github/workflows/publish.yml`` and
  ``test_publish.yml`` now build/publish on Python 3.12 (previously 3.8, which is no longer
  installable per ``python_requires``) and got their ``actions/checkout`` bumped to v4;
  updated the stale ``mkvirtualenv -p python3.8`` instruction in ``README.rst`` and the
  Python intersphinx mapping in ``docs/conf.py`` to point at 3.12.

3.8.9 - 2026-08-21
**********************************************
* Completed DataDog instrumentation for Xpert Summary (LP-919): config API requests
  (``ai_aside/config_api/views.py``) are now instrumented centrally in
  ``AiAsideAPIView``, tagged with method/course_id/unit_id/action/status and
  reporting call counts and latency; ``summary_handler`` now reports invocation
  counts, content-extraction latency, content size, and block count; and
  ``student_view_aside`` now reports aside injection counts and render latency
  tagged with user_role. Added a Datadog querying/alerting reference doc
  (``docs/how-tos/monitoring.rst``).

* Added DataDog monitoring for Xpert Summary: render failures, should_apply_to_block
  failures, and summary_handler request outcomes are now reported as custom attributes,
  counters, and monitored exceptions instead of only being logged.

3.8.8 - 2026-08-05
**********************************************
* Added Django 5.2 tox/CI compatibility and Python 3.11 test matrix updates.

3.8.7 - 2026-07-28
**********************************************
* Gave the Xpert Unit Summary button and panel a light note-box look, scoped to
  the ai-aside rendering (kept out of ai-spot since it's also embedded by
  non-edX consumers)

3.8.6 - 2026-03-24
**********************************************
* Fixed is_summary_enabled() to properly check course-level settings when no unit record exists
* This ensures course-level toggle correctly controls summary button visibility

3.8.5 - 2026-02-10
**********************************************
* Added client ID support for unit summary feature
* Updated build process to use python -m build instead of setup.py

3.8.2 - 2025-05-14
**********************************************
* Fixed bug where necessary class variables were not set on the AiAsideCourseApp class

3.8.1 - 2025-05-13
**********************************************
* Bumped ubuntu version to latest for the PyPi publishing job

3.8.0 - 2025-05-07
**********************************************
* Added setting to control whether the summary should be enabled by default
* Bumped actions/setup-python from 4 to 5
* Added setting to set the default enabled state for course summaries
* Updated readme deployment section
* Added course_app/plugin for unit summaries

3.7.0 — 2023-11-20
**********************************************
* Moved standard error handling to where it will not bother newrelic

3.6.2 — 2023-10-12
**********************************************

* Handle rare blocks missing dates when calculating last updated
* Remove log of expected "not here" exception during config

3.6.1 — 2023-10-10
**********************************************

* Resolve scenario where a user has no associated enrollment value

3.6.0 – 2023-10-05
**********************************************

* Include user role in summary hook HTML.
* Add make install-local target for easy devstack installation.

3.5.0 – 2023-09-04
**********************************************

* Add edx-drf-extensions lib.
* Add JwtAuthentication checks before each request.
* Add SessionAuthentication checks before each request.
* Add HasStudioWriteAccess permissions checks before each request.


3.4.0 – 2023-08-30
**********************************************

* Include last updated timestamp in summary hook HTML, derived from the blocks.
* Also somewhat reformats timestamps in the handler return to conform to ISO standard.


3.3.1 – 2023-08-21
**********************************************

* Remove no longer needed first waffle flag summaryhook_enabled

3.3.0 – 2023-08-16
**********************************************

Features
=========
* Add xpert summaries configuration by default for units

3.2.0 – 2023-07-26
**********************************************

Features
=========
* Added the checks for the module settings behind the waffle flag `summaryhook.summaryhook_summaries_configuration`.
* Added is this course configurable endpoint
* Error suppression logs now include block ID
* Missing video transcript is caught earlier in content fetch

3.1.0 – 2023-07-20
**********************************************

Features
=========

* Added API endpoints for updating settings for courses and modules (enable/disable for now) (Has migrations)

3.0.1 – 2023-07-20
**********************************************

* Add positive log when summary fragement decides to inject

3.0.0 – 2023-07-16
**********************************************

Features
=========
* Summary content handler now requires a staff user identity, otherwise returns 403. This is a breaking change.
* Added models to summaryhook_aside (Has migrations)
* Catch exceptions in a couple of locations so the aside cannot crash content.

2.0.2 – 2023-07-05
**********************************************

Fix
=====

* Updated HTML parser to remove tags with their content for specific cases like `<script>` or `<style>`.


2.0.1 – 2023-06-29
**********************************************

Fix
=====

* Fix transcript format request and conversion


2.0.0 – 2023-06-28
**********************************************

Added
=====

* Adds a handler endpoint to provide summarizable content
* Improves content length checking using that summarizable content


1.2.1 – 2023-05-19
**********************************************

Fixes
=====

* Fix summary-aside settings package

1.2.0 – 2023-05-11
**********************************************

Added
=====

* Porting over summary-aside from edx-arch-experiments version 1.2.0
