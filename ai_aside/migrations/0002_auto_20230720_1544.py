# Generated by Django 3.2.20 on 2023-07-20 15:44

from django.db import migrations
import opaque_keys.edx.django.models


class Migration(migrations.Migration):

    dependencies = [
        ('ai_aside', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='aiasidecourseenabled',
            options={},
        ),
        migrations.AlterModelOptions(
            name='aiasideunitenabled',
            options={},
        ),
        migrations.AlterField(
            model_name='aiasidecourseenabled',
            name='course_key',
            field=opaque_keys.edx.django.models.CourseKeyField(db_index=True, max_length=255, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='aiasideunitenabled',
            unique_together={('course_key', 'unit_key')},
        ),
    ]
