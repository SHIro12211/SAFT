from django.contrib.auth.models import (
    AbstractBaseUser, AbstractUser
)
from django.core.validators import (MinLengthValidator, MaxLengthValidator)
from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.

# modelos relacionados con los activos fijos
class Office(models.Model):
    number = models.CharField(
        _('Nombre de Oficina'),
        help_text='[Nombre o número descriptivo de la oficina]',
        max_length=30,
        null=True,
        blank=False,
        unique=True
    )
    id_area = models.PositiveIntegerField(
        _('Área'),
        null=True
    )
    description = models.TextField(
        _('Observaciones'),
        null=True,
        blank=True
    )

    def __str__(self):
        if self.description:
            return str(self.number) + "---" + str(self.description)
        else:
            return str(self.number)

    class Meta:
        verbose_name = _('Oficina')
        verbose_name_plural = _('Oficinas')


class FixedAssetType(models.Model):
    type_FixedAsset = models.CharField(
        _('Tipo'),
        max_length=100,
        unique=True
    )

    def __str__(self):
        return self.type_FixedAsset

    class Meta:
        verbose_name = _('Tipo de Activo Fijo')
        verbose_name_plural = _('Tipos de Activos Fijos')


class FixedAssetStatu(models.Model):
    statu = models.CharField(
        _('Estado'),
        max_length=1,
        unique=True
    )

    def __str__(self):
        return self.statu.upper()

    class Meta:
        verbose_name = _('Estado')
        verbose_name_plural = _('Estados')


class FixedAsset(models.Model):
    stock_number = models.CharField(
        _('Número de inventario'),
        unique=True,
        help_text='[6-10]',
        max_length=10,
        validators=[MinLengthValidator(6, 'Debe ser mayor que 6 digitos'),
                    MaxLengthValidator(10, 'Debe ser menor que 10 digitos')]
    )
    id_fixed_asset_type = models.ForeignKey(
        FixedAssetType,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        verbose_name=_('Tipo')
    )
    model = models.CharField(
        _('Modelo'),
        null=True,
        blank=True,
        max_length=25,
        help_text='[A-Z, 0-8, -]'
    )
    brand = models.CharField(
        _('Marca'),
        null=True,
        blank=True,
        max_length=100
    )
    serial_number = models.CharField(
        _('Número de serie'),
        null=True,
        blank=True,
        max_length=200
    )
    id_statu = models.ForeignKey(
        FixedAssetStatu,
        on_delete=models.CASCADE,
        verbose_name=_('Estado'),
        blank=False,
        null=False
    )
    id_office = models.ForeignKey(
        Office,
        on_delete=models.CASCADE,
        verbose_name=_('Oficina'),
        blank=False,
        null=False
    )
    observations = models.TextField(
        _('Observaciones'),
        null=True,
        blank=True,
    )

    last_update = models.DateField(
        _('Ultima actualización'),
        auto_now=True,
    )
    is_active = models.BooleanField(
        _('En uso'),
        default=True
    )

    id_worker = models.ManyToManyField(
        to='people.Worker',
        blank=True,
        null=True,
        verbose_name=_('Trabajador'),
    )

    def __str__(self):
        return 'AFT No. ' + str(self.stock_number)

    class Meta:
        verbose_name = _('Activo Fijo')
        verbose_name_plural = _('Activos Fijos')

        permissions = (
            ('can_view_all_fixedasset', ('Can view all Fixed Asset')),
            ('can_view_the_dpto_fixedasset', ('Can view the dpto Fixed Asset')),
        )
