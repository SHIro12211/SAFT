# Generated by Django 4.1.2 on 2023-02-02 15:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0007_remove_worker_id_fixed_asset'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='department',
            options={'verbose_name': 'Departamento', 'verbose_name_plural': 'Departamentos'},
        ),
        migrations.AlterModelOptions(
            name='headarea',
            options={'verbose_name': 'Jefe de área', 'verbose_name_plural': 'Jefes de áreas'},
        ),
        migrations.AlterModelOptions(
            name='headdepartment',
            options={'verbose_name': 'Jefe de departamento', 'verbose_name_plural': 'Jefes de departamentos'},
        ),
        migrations.AlterModelOptions(
            name='worker',
            options={'verbose_name': 'Trabajador', 'verbose_name_plural': 'Trabajadores'},
        ),
        migrations.AlterField(
            model_name='department',
            name='name',
            field=models.CharField(max_length=100, unique=True, verbose_name='Departamento'),
        ),
        migrations.AlterField(
            model_name='headarea',
            name='id_area',
            field=models.PositiveIntegerField(verbose_name='Área'),
        ),
        migrations.AlterField(
            model_name='headarea',
            name='id_worker',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='people.worker', verbose_name='Jefe de área'),
        ),
        migrations.AlterField(
            model_name='headdepartment',
            name='id_department',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='people.department', verbose_name='Jefes de departamentos'),
        ),
        migrations.AlterField(
            model_name='headdepartment',
            name='id_worker',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='people.worker', verbose_name='Jefe de departamento'),
        ),
        migrations.AlterField(
            model_name='worker',
            name='id_department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.department', verbose_name='Departamento'),
        ),
        migrations.AlterField(
            model_name='worker',
            name='id_person',
            field=models.PositiveIntegerField(unique=True, verbose_name='Trabajador'),
        ),
        migrations.AlterField(
            model_name='worker',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Activo'),
        ),
        migrations.AlterField(
            model_name='worker',
            name='mail',
            field=models.EmailField(max_length=254, verbose_name='Correo'),
        ),
    ]
