from dal import autocomplete
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, UserCreationForm
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as filters

from saft.apps.people.models import Worker, HeadArea, Department, HeadDepartment
from saft.apps.people.widget import DepartmetSelect, WorkerSelect
from saft.settings.base import GraphqlService


# !--------------ADMIN--------------------------
class WorkerFormAdmin(forms.ModelForm):  # clase formulario de worker del admin
    class Meta:
        model = Worker
        fields = ['id_person', 'id_department', 'mail', 'is_active']
        widgets = {
            'id_person': autocomplete.ListSelect2(url='admin:people_user_personcomplete'),
            'id_department': forms.Select(),
            'mail': forms.EmailInput()
        }


class HeadAreaForm(forms.ModelForm):  # clase formulario del HeadArea en el admin
    class Meta:
        model = HeadArea
        fields = ['id_worker', 'id_area']
        widgets = {
            'id_area': autocomplete.ListSelect2(url='admin:people_head_area_personcomplete'),
        }


class DepartmentForm(forms.ModelForm):  # clase formulario de department del admin
    class Meta:
        model = Department
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),

        }


class HeadDepartmentForm(forms.ModelForm):  # clase formulario de HeadDepartment del admin
    class Meta:
        model = HeadDepartment
        fields = ['id_worker', 'id_department']
        widgets = {
            'id_worker': WorkerSelect(attrs={'class': 'form-select form-select-sm'}),
            'id_department': DepartmetSelect(attrs={'class': 'form-select form-select-sm'}),
        }


# !----------------------------------------
class HeadDepartmentWorkerForm(forms.ModelForm):  # clase formulario del worker en saft
    class Meta:
        model = Worker
        fields = ['id_person', 'mail', 'is_active']
        widgets = {
            'id_person': forms.Select(attrs={'class': 'form-select form-select-sm'},
                                      choices=GraphqlService().get_all_person_to_choice()),
            'mail': forms.EmailInput(attrs={'class': 'form-control form-control-sm'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input', 'type': 'checkbox'})
        }

    def clean_id_person(self):
        person = self.cleaned_data['id_person']
        if person == 0:
            raise ValidationError("Este campo es obligatorio.")
        return person



class WorkerForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = ['id_person', 'id_department', 'mail', 'is_active']
        widgets = {
            'id_person': forms.Select(attrs={'class': 'form-select form-select-sm'},
                                      choices=GraphqlService().get_all_person_to_choice()),

            'id_department': DepartmetSelect(attrs={'class': 'form-select form-select-sm'}),
            'mail': forms.EmailInput(attrs={'class': 'form-control form-control-sm'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input', 'type': 'checkbox'})
        }

    def clean_id_person(self):
        person = self.cleaned_data['id_person']
        if person == 0:
            raise ValidationError("Este campo es obligatorio.")
        return person


# !-------------------LOGIN------------------------------
class MyLoginForm(AuthenticationForm):  # clase formulario del Login
    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    error_messages = {
        "invalid_login": (
            "Please enter a correct %(username)s and password. Note that both "
            "fields may be case-sensitive."
        ),
        "inactive": ("This account is inactive."),
        'unauthenticated': 'Usted no esta auntenificado. Por favor ingresse los datos solicitados'
    }


# !-----------------------------------------------------
''' conjunto de clases formularios que permiten que puedas 
 usar la libreria de autocomplete-ligth para el select de person en User'''


class MixinForm(forms.ModelForm):
    person = autocomplete.Select2ListCreateChoiceField(
        required=True,
        widget=autocomplete.ListSelect2(url='admin:people_user_personcomplete')
    )


class UserChangeMixinForm(UserChangeForm, MixinForm):
    pass


class UserCreationMixinForm(UserCreationForm, MixinForm):
    pass


# !-----------------------------------------------------
# !-------------------DJANGO-FILTER--------------------
class WorkerFilter(filters.FilterSet):  # clase formulario que usa la libreria django-filter
    id_person = filters.Filter(label=_('Nombre del Trabajador'), method='find_id_person')
    id_department = filters.ModelChoiceFilter(queryset=Department.objects.all())

    def find_id_person(self, queryset, name, value):
        '''parametros: queryset es  el queryset que filtra
                       name es el nombre del campo a filtrar
                       value es el valor ingresado en el input'''
        res_grafph = GraphqlService().get_person_by_name(value)
        res_querset = queryset.none()
        for item in res_grafph:
            res_querset = res_querset | queryset.filter(id_person=item['id'])
        return res_querset

    class Meta:
        model = Worker
        fields = ['id_person', 'id_department']
