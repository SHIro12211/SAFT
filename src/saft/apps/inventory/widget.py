from django import forms
from django.core.cache import cache
from django.shortcuts import get_object_or_404

from saft.apps.inventory.models import Office
from saft.apps.people.models import Worker


class WorkerMultiSelect(forms.SelectMultiple):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(
            name, value, label, selected, index, subindex, attrs
        )
        person = cache.get('user_loger')
        try:
            user_worker = get_object_or_404(Worker, id_person=person['id'])
        except:
            return super().create_option(
                '', '', '', '', '', '', ''
            )
        else:
            qs_worker = Worker.objects.filter(id_department__id_area__exact=user_worker.id_department.id_area).filter(
                is_active=True)
            for worker in qs_worker:
                if str(worker.id_person) == str(label):
                    return option
            return super().create_option(
                '', '', '', '', '', '', ''
            )


class WorkerMultiSelectHD(forms.SelectMultiple):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(
            name, value, label, selected, index, subindex, attrs
        )
        person = cache.get('user_loger')
        try:
            user_worker = get_object_or_404(Worker, id_person=person['id'])
        except:
            return super().create_option(
                '', '', '', '', '', '', ''
            )
        else:
            qs_worker = Worker.objects.filter(id_department_id__exact=user_worker.id_department.id).filter(
                is_active=True)
            for worker in qs_worker:
                if str(worker.id_person) == str(label):
                    return option
            return super().create_option(
                '', '', '', '', '', '', ''
            )


class OfficeSelect(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(
            name, value, label, selected, index, subindex, attrs
        )
        person = cache.get('user_loger')
        if value:
            office = get_object_or_404(Office, id=int(str(value)))
            if office.id_area == int(person['area']['id']):
                return option
            else:
                return super().create_option(
                    '', '', '', '', '', '', ''
                )
        return option
