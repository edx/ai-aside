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
