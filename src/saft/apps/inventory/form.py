from django import forms
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django_filters import rest_framework as filters

from .models import FixedAsset, FixedAssetType, Office, FixedAssetStatu
# !------------Admin-----------------------------
from .widget import WorkerMultiSelect, OfficeSelect, WorkerMultiSelectHD


class FixedAssetFormSimpleuser(forms.ModelForm):
    class Meta:
        model = FixedAsset
        fields = ['stock_number', 'serial_number', 'model', 'brand', 'id_statu', 'id_office', 'id_fixed_asset_type',
                  'is_active', 'observations']
        widgets = {
            'stock_number': forms.TextInput(
                attrs={'class': 'form-control form-control-sm'}),
            'serial_number': forms.NumberInput(
                attrs={'class': 'form-control form-control-sm'}),
            'model': forms.TextInput(
                attrs={'class': 'form-control form-control-sm'}),
            'brand': forms.TextInput(
                attrs={'class': 'form-control form-control-sm'}),
            'id_statu': forms.Select(
                attrs={'class': 'form-select  form-select-sm'}),
            'id_office': OfficeSelect(
                attrs={'class': 'form-select form-select-sm'}),
            'id_fixed_asset_type': forms.Select(
                attrs={'class': 'form-select form-select-sm'}),
            'is_active': forms.CheckboxInput(
                attrs={'class': 'form-check-input', 'type': 'checkbox'}),
            'observations': forms.Textarea
            (attrs={'class': 'form-control', 'rows': '3'}),
        }

    def clean_stock_number(self):  # validación de número de inventario
        stock_number = self.cleaned_data['stock_number']
        print(stock_number)
        if not stock_number.isnumeric():
            raise ValidationError("Solo caracteres numéricos.")
        return stock_number

    def clean_model(self):  # validación de modelo, no debe tener ningun caracter exeptos alfanumericos y guiones
        flag = False
        model = self.cleaned_data['model']
        if model:
            for char in model:
                if char == '-':
                    flag = True
                    break
            if flag:
                split_model = model.split('-')
                for sub_list in split_model:
                    if sub_list:
                        if not sub_list.isalnum():
                            raise ValidationError("Solo caracteres numéricos, alfabeticos y .")
            elif not model.isalnum():
                raise ValidationError("Solo caracteres numéricos, alfabeticos o guión largo .")
        return model


class FixedAssetForm(FixedAssetFormSimpleuser):  # clase formulario de FixedAsset de admin y de saft
    class Meta:
        model = FixedAsset
        fields = ['stock_number', 'serial_number', 'model', 'brand', 'id_statu', 'id_office', 'id_fixed_asset_type',
                  'id_worker', 'is_active', 'observations']

        widgets = {
            'stock_number': forms.TextInput(
                attrs={'class': 'form-control form-control-sm'}),
            'serial_number': forms.NumberInput(
                attrs={'class': 'form-control form-control-sm'}),
            'model': forms.TextInput(
                attrs={'class': 'form-control form-control-sm'}),
            'brand': forms.TextInput(
                attrs={'class': 'form-control form-control-sm'}),
            'id_statu': forms.Select(
                attrs={'class': 'form-select  form-select-sm'}),
            'id_office': OfficeSelect(
                attrs={'class': 'form-select form-select-sm'}),
            'id_fixed_asset_type': forms.Select(
                attrs={'class': 'form-select form-select-sm'}),
            'id_worker': WorkerMultiSelect(
                attrs={'class': 'form-select form-select-sm'}),
            'is_active': forms.CheckboxInput(
                attrs={'class': 'form-check-input', 'type': 'checkbox'}),
            'observations': forms.Textarea
            (attrs={'class': 'form-control', 'rows': '3'}),
        }


class FixedAssetHeadDepartmentForm(FixedAssetFormSimpleuser):  # clase formulario de FixedAsset de admin y de saft
    class Meta:
        model = FixedAsset
        fields = ['stock_number', 'serial_number', 'model', 'brand', 'id_statu', 'id_office', 'id_fixed_asset_type',
                  'id_worker', 'is_active', 'observations']

        widgets = {
            'stock_number': forms.TextInput(
                attrs={'class': 'form-control form-control-sm'}),
            'serial_number': forms.NumberInput(
                attrs={'class': 'form-control form-control-sm'}),
            'model': forms.TextInput(
                attrs={'class': 'form-control form-control-sm'}),
            'brand': forms.TextInput(
                attrs={'class': 'form-control form-control-sm'}),
            'id_statu': forms.Select(
                attrs={'class': 'form-select  form-select-sm'}),
            'id_office': OfficeSelect(
                attrs={'class': 'form-select form-select-sm'}),
            'id_fixed_asset_type': forms.Select(
                attrs={'class': 'form-select form-select-sm'}),
            'id_worker': WorkerMultiSelectHD(
                attrs={'class': 'form-select form-select-sm'}),
            'is_active': forms.CheckboxInput(
                attrs={'class': 'form-check-input', 'type': 'checkbox'}),
            'observations': forms.Textarea
            (attrs={'class': 'form-control', 'rows': '3'}),
        }


class FixedAssetTypeForm(forms.ModelForm):  # clase formulario de TypeFixedAsset fijo en el admin
    class Meta:
        model = FixedAssetType
        fields = ['type_FixedAsset']

        widgets = {
            'type_FixedAsset': forms.TextInput(
                attrs={'class': 'form-control form-control-sm'}),
        }


class OfficeForm(forms.ModelForm):  # clase formulario de office en el admin
    class Meta:
        model = Office
        fields = ['number', 'description']
        widgets = {
            'number': forms.TextInput(
                attrs={'class': 'form-control form-control-sm'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'rows': '3'}),
        }


# !------------Admin-----------------------------

# !--------------Django Filter---------------------------

PERSON = cache.get('user_loger')


class FixedAssetFilter(filters.FilterSet):  # clase formulario de FixedAsset
    stock_number = filters.CharFilter(method='find_stock_number_fixedasset')
    brand = filters.CharFilter()
    id_office = filters.ModelChoiceFilter(queryset=Office.objects.all())
    id_statu = filters.ModelChoiceFilter(queryset=FixedAssetStatu.objects.all())
    id_fixed_asset_type = filters.ModelChoiceFilter(queryset=FixedAssetType.objects.all())

    class Meta:
        model = FixedAsset
        fields = ['stock_number', 'brand', 'id_office', 'id_statu', 'id_fixed_asset_type']

    def find_stock_number_fixedasset(self, queryset, name, value):
        res_querset = queryset.none()
        res_querset = res_querset | queryset.filter(stock_number__contains=value)
        return res_querset


class FixedAssetFilterUser(FixedAssetFilter):  # clase de FisedAsset del user auntentificado(pendiente)
    # id_office = filters.ModelChoiceFilter(queryset=office)
    pass


class OfficeFilter(filters.FilterSet):  # clase de FisedAsset del user auntentificado(pendiente)
    number = filters.NumberFilter()

    class Meta:
        model = Office
        fields = ['number']

# !--------------Django Filter---------------------------
