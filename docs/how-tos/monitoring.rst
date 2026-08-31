Querying and Alerting on ai-aside Metrics in Datadog
######################################################

ai-aside emits custom metrics through ``edx_django_utils.monitoring``, which
forwards them to New Relic/Datadog. The functions that emit them live in
``ai_aside/monitoring.py`` -- see that module's docstrings for exactly what
each one tags and when it's called.

Metric reference
*****************

Config API (``ai_aside/config_api/views.py``, instrumented centrally in
``AiAsideAPIView``):

``ai_aside.config_api.requests`` / ``ai_aside.config_api.requests.<status>``
  Call count for every GET/POST/DELETE to ``/ai_aside/v1/:course_id[/:unit_id]``,
  tagged with ``method``, ``course_id``, ``unit_id``, ``action`` (``read`` /
  ``enable`` / ``disable`` / ``update`` / ``reset``), and ``status``
  (``success`` / ``unauthenticated`` / ``forbidden`` / ``not_found`` /
  ``client_error`` / ``error``).
``ai_aside.config_api.duration_ms``
  Request latency.

Summary Handler (``ai_aside/block.py``, ``summary_handler``):

``ai_aside.handler.requests``
  Total invocation count, including requests later rejected.
``ai_aside.handler.extraction_time`` / ``.extraction_time_ms``
  Time spent in ``_parse_children_contents`` (accumulated counter / per-request attribute).
``ai_aside.handler.content_size`` / ``.block_count``
  Bytes extracted and child blocks that yielded content, per call.
``xpert_summary.handler.{forbidden,not_found,empty,success,error}``
  Request outcome, one series per outcome.

Block Injection (``ai_aside/block.py``, ``student_view_aside``):

``ai_aside.aside.injections``
  Incremented each time the aside is actually rendered into a unit. Tagged with
  ``course_id``, ``unit_id``, ``user_role``.
``ai_aside.aside.render_time`` / ``.render_time_ms``
  Wall-clock time to extract content and render the fragment.
``ai_aside.aside.extraction_errors``
  Extraction failures from either the handler or aside path, tagged with
  ``ai_aside.extraction.source`` (``handler`` / ``aside``) and ``.error_class``.
``xpert_summary.render.error``
  ``student_view_aside`` suppressed an exception (any cause, not just extraction).

Building Datadog widgets and monitors
***************************************

#. **Traffic/latency**: timeseries on ``ai_aside.config_api.requests`` or
   ``ai_aside.handler.requests``, grouped by ``course_id``/``action``/``status``;
   pair with the ``duration_ms``/``extraction_time_ms``/``render_time_ms``
   attributes (p50/p95/p99) for latency.
#. **Content size**: chart ``ai_aside.handler.content_size`` /
   ``.block_count`` to catch unusually large units driving slow extractions.
#. **Injection rate**: ``ai_aside.aside.injections`` grouped by ``user_role``.

Suggested monitors:

* **Config API error rate**: alert on ``sum:ai_aside.config_api.requests.error``
  (or ``client_error``/``forbidden``) over ``sum:ai_aside.config_api.requests``.
* **Handler error rate**: alert on ``sum:xpert_summary.handler.error`` (hard 500s).
* **Extraction error rate**: alert on ``sum:ai_aside.aside.extraction_errors``,
  split by ``ai_aside.extraction.source``.
* **Latency regression**: alert on p95 of ``ai_aside.handler.extraction_time_ms``
  or ``ai_aside.aside.render_time_ms``.

Exceptions and trace context
******************************

Every monitoring function that reports an error also calls
``record_exception()``, attaching the exception to the current APM trace
context so it shows up in Datadog's Error Tracking linked to the originating
request, not just in application logs.
