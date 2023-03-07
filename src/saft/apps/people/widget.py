from django import forms
from django.core.cache import cache
from django.shortcuts import get_object_or_404

from saft.apps.people.models import Department, Worker


class DepartmetSelect(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(
            name, value, label, selected, index, subindex, attrs
        )
        person = cache.get('user_loger')
        if type(value) != type(''):
            dpto = get_object_or_404(Department, id=int(str(value)))
            if str(dpto.id_area) == str(person['area']['id']):
                return option
            else:
                return super().create_option(
                    '', '', '', '', '', '', ''
                )
        return option


class WorkerSelect(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(
            name, value, label, selected, index, subindex, attrs
        )
        person = cache.get('user_loger')
        print(value)
        if type(value) != type(''):
            worker = get_object_or_404(Worker, id=int(str(value)))
            if str(worker.id_department.id_area) == str(person['area']['id']):
                return option
            else:
                return super().create_option(
                    '', '', '', '', '', '', ''
                )
        return option
