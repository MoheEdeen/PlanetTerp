# Generated by Django 3.2.5 on 2021-08-20 02:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0024_alter_userschedule_section'),
    ]

    operations = [
        migrations.AddField(
            model_name='professor',
            name='courses',
            field=models.ManyToManyField(through='home.ProfessorCourse', to='home.Course'),
        ),
    ]