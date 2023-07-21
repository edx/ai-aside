"""
AI Aside block models.
"""

from django.db import models
from opaque_keys.edx.django.models import CourseKeyField, UsageKeyField


class AIAsideCourseEnabled(models.Model):
    """
    Maps Course Key to enabled boolean.
    """

    course_key = CourseKeyField(db_index=True, max_length=255, unique=True)
    enabled = models.BooleanField(default=False, null=False)

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Query."""
        return (
            "id={id} "
            "created={created} "
            "course_key={course_key} "
            "enabled={enabled}".format(
                id=self.id,
                created=self.created.isoformat(),
                course_key=self.course_key,
                enabled=self.enabled,
            )
        )


class AIAsideUnitEnabled(models.Model):
    """
    Maps a Unit Key to enabled boolean.
    """

    course_key = CourseKeyField(db_index=True, max_length=255)
    unit_key = UsageKeyField(db_index=True, max_length=255)
    enabled = models.BooleanField(default=False, null=False)

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        """Course and unit are unique together."""

        unique_together = ('course_key', 'unit_key')

    def __str__(self):
        """Query."""
        return (
            "id={id} "
            "created={created} "
            "course_key={course_key} "
            "unit_key={unit_key} "
            "enabled={enabled}".format(
                id=self.id,
                created=self.created.isoformat(),
                course_key=self.course_key,
                unit_key=self.unit_key,
                enabled=self.enabled,
            )
        )
