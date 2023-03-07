from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


# modelos que giran alrededor de la api identidades
class Department(models.Model):
    name = models.CharField(
        _('Nombre'),
        unique=True,
        max_length=100
    )
    id_area = models.PositiveIntegerField(
        _('Nombre del Área'),
        blank=False,
        null=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Departamento')
        verbose_name_plural = _('Departamentos')


class Worker(models.Model):
    id_person = models.PositiveIntegerField(
        _('Trabajador'),
        unique=True,
        blank=False,
        null=False,
    )
    mail = models.EmailField(
        _('Correo'),
    )
    id_department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        verbose_name=_('Departamento'),

    )
    is_active = models.BooleanField(
        _('Activo'),
        default=True
    )

    def __str__(self):
        return str(self.id_person)

    class Meta:
        verbose_name = _('Trabajador')
        verbose_name_plural = _('Trabajadores')


class HeadArea(models.Model):
    id_worker = models.OneToOneField(
        Worker,
        on_delete=models.CASCADE,
        verbose_name=_('Jefe de área')
    )
    id_area = models.PositiveIntegerField(
        _('Área')
    )

    def __str__(self):
        return str(self.id_worker)

    class Meta:
        verbose_name = _('Jefe de área')
        verbose_name_plural = _('Jefes de áreas')


class HeadDepartment(models.Model):
    id_worker = models.OneToOneField(
        Worker,
        on_delete=models.CASCADE,
        verbose_name=_('Trabajador')
    )
    id_department = models.OneToOneField(
        Department,
        on_delete=models.CASCADE,
        verbose_name=_('Departamentos   ')
    )

    def __str__(self):
        return str(self.id_worker)

    class Meta:
        verbose_name = _('Jefe de departamento')
        verbose_name_plural = _('Jefes de departamentos')


class User(AbstractUser):  # Usuario en el sistema
    person = models.PositiveIntegerField('User', null=True, blank=True)

    class Meta:
        # !para que el campo sea unico
        constraints = [models.UniqueConstraint(fields=['person'], name='unique person')]
        verbose_name = 'User'
        verbose_name_plural = 'Users'
