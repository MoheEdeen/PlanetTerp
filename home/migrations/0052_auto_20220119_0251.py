# Generated by Django 3.2.4 on 2022-01-19 02:51

from django.db import migrations, models
from django.db.models.functions import Concat


def forwards_func(apps, _schema_editor):
    Course = apps.get_model("home", "Course")
    Course.objects.all().update(name=Concat("department", "course_number"))

class Migration(migrations.Migration):

    dependencies = [
        ('home', '0051_auto_20220119_0241'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='course',
            name='unique_course_name',
        ),
        migrations.RemoveIndex(
            model_name='course',
            name='home_course_departm_4b085e_idx',
        ),
        migrations.RemoveIndex(
            model_name='course',
            name='home_course_course__b31247_idx',
        ),
        migrations.AddField(
            model_name='course',
            name='name',
            field=models.CharField(default='temp', max_length=10),
            preserve_default=False,
        ),
        migrations.RunPython(forwards_func),
        migrations.AddIndex(
            model_name='course',
            index=models.Index(fields=['name'], name='home_course_name_60420f_idx'),
        ),
        migrations.AddConstraint(
            model_name='course',
            constraint=models.UniqueConstraint(fields=('name',), name='unique_course_name'),
        ),
    ]