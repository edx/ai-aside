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
