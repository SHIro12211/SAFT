# Generated by Django 4.1.2 on 2023-02-21 20:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0008_alter_department_options_alter_headarea_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='name',
            field=models.CharField(max_length=100, unique=True, verbose_name='Nombre'),
        ),
    ]
