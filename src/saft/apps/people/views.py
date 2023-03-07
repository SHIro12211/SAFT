import socket

from dal import autocomplete
# Create your views here.
from decouple import config
from django.contrib import messages
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views import generic

from saft.apps.inventory.models import FixedAsset, Office
from saft.apps.inventory.views import BaseListView, BaseAddView, BaseUpdateView, DeleteBaseView, DetaiBaseView
from saft.apps.people.form import WorkerForm, WorkerFilter, HeadDepartmentWorkerForm, DepartmentForm, HeadDepartmentForm
from saft.apps.people.models import Worker, Department, HeadDepartment
from saft.settings.base import GraphqlService

# ----------------------------------------------------------------

'''confunto de clases vistas de autocompete-ligth'''


class PersonAutocompleteView(autocomplete.Select2ListView):

    def get_list(self):
        graf = cache.get('all_person')
        if not graf:
            graf = GraphqlService().get_all_person_to_choice()
        return graf


class IdAreaAutocompleteView(autocomplete.Select2ListView):

    def get_list(self):
        return GraphqlService().area_to_choice()


# ----------------------------------------------------------------
def user_cache(user):
    if not cache.get('user_loger'):
        cache.set('user_loger', GraphqlService().get_person_by_id(user.person))
    return cache.get('user_loger')


# ----------------LIST-----------------------------------------------------
class WorkerListView(BaseListView):
    model = Worker
    add_url = 'people/addworker/'
    update_url = 'people/updateworker/'

    def get(self, request, *args, **kwargs):
        cache.set('user_loger', GraphqlService().get_person_by_id(request.user.person))

        if not request.user.has_perm('inventory.can_view_the_dpto_fixedasset') and not request.user.has_perm(
                'inventory.can_view_all_fixedasset'):
            raise PermissionDenied

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        ''':return devuelve un queryset de trabajadores segun los permisos del usuario auntentificado'''
        qs_worker = []
        if self.request.user.has_perm('inventory.can_view_all_fixedasset'):  # si el user es un Jefe de Area
            person = user_cache(self.request.user)
            qs_worker = Worker.objects.filter(id_department__id_area__exact=person['area']['id']).filter(is_active=True)
        elif self.request.user.has_perm('inventory.can_view_the_dpto_fixedasset'):  # si es Jefe de Dpto
            # id del departamento del user auntentificado en el sistema
            try:
                id_department_worker = get_object_or_404(Worker,
                                                         id_person__exact=self.request.user.person).id_department.id
            except:
                messages.error(self.request, _('Usted no es un Jefe de Departamento en el sistema'))
                return Worker.objects.none()
            else:
                # queryset de trabajadores del mismo departamento que el user autentificado, exepto el mismo user
                qs_worker = Worker.objects.filter(id_department_id__exact=id_department_worker).filter(is_active=True)
        else:
            qs_worker = Worker.objects.none()
        return qs_worker.order_by('id').reverse()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        person = cache.get('user_loger')
        # clase filtro del django-filter que recibe una solicitud GET y el queryset que deseas filtrar
        f = WorkerFilter(self.request.GET, self.get_queryset())
        # paginar el queryset por parametro, o sea el queryset del django-filter recibido
        page_size = self.get_paginate_by(f.qs)
        if page_size:
            paginator, page, queryset, is_paginated = self.paginate_queryset(f.qs, page_size)
        # para crear un encabezado generico, pero añado al final una columna que no es un campo del modelo worker
        new_enc = self.get_all_field(4)[:3]
        if self.request.user.has_perm('inventory.can_view_the_dpto_fixedasset'):
            new_enc.remove('Departamento')
            var = _('Departamento')
        else:
            var = _('Área')
        qs_dpto = Department.objects.filter(id_area__exact=int(person['area']['id']))
        new_enc.append(_('Cantidad de AF'))
        context['enc'] = new_enc
        context['filter'] = f
        context['w'] = 'true'
        context['page_obj'] = page
        context['name'] = _('Trabajadores del ') + var
        context['title'] = _('Tabla de Trabajadores')
        context['object_list'] = queryset
        context['dpto_list'] = qs_dpto
        # url de la api de identidades
        context['api_url'] = config('API_URL')
        return context


class DepartmentListView(BaseListView):
    model = Department
    add_url = 'people/others/adddepartment/'
    update_url = 'people/others/updatedepartment/'

    def get(self, request, *args, **kwargs):
        try:
            is_person_user = request.user.person
        except:
            return redirect('/?next=%s' % request.path)
        else:
            if not request.user.has_perm('inventory.can_view_all_fixedasset'):
                raise PermissionDenied
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        person = user_cache(self.request.user)
        return Department.objects.filter(id_area__exact=int(person['area']['id'])).order_by('id').reverse()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        page_size = self.get_paginate_by(self.get_queryset())
        if page_size:
            paginator, page, queryset, is_paginated = self.paginate_queryset(self.get_queryset(), page_size)
        # para crear un encabezado generico, pero añado al final una columna que no es un campo del modelo worker
        context['enc'] = [_('Nombre'), _('Jefe del Dpto.'), _('Cantidad de Trabajadores'),
                          _('Cantida de Activos Fijos')]
        list_object_list = []
        for qs in queryset:
            count = FixedAsset.objects.filter(id_worker__id_department_id__exact=qs.id).count()
            list_object_list.append({
                'object_list': qs,
                'cant_fa': count
            })
        context['page_obj'] = page
        context['dpto'] = 'true'
        context['name'] = _('Departamentos')
        context['title'] = _('Tabla de Departamentos')
        context['object_list'] = list_object_list
        return context


class WorkerListDisabledView(WorkerListView):

    def get_queryset(self):
        qs_worker = []
        person = cache.get('user_loger')
        if self.request.user.has_perm('inventory.can_view_all_fixedasset'):  # si el user es un Jefe de Area
            qs_worker = Worker.objects.filter(is_active=False).filter(
                id_department__id_area__exact=int(person['area']['id']))
        elif self.request.user.has_perm('inventory.can_view_the_dpto_fixedasset'):  # si es Jefe de Dpto
            # id del departamento del user auntentificado en el sistema
            try:
                id_department_worker = get_object_or_404(Worker,
                                                         id_person__exact=self.request.user.person).id_department.id
            except:
                messages.error(self.request, _('Usted no es un Jefe de Departamento en el sistema'))
                return Worker.objects.none()
            else:
                # queryset de trabajadores del mismo departamento que el user autentificado, exepto el mismo user
                qs_worker = Worker.objects.filter(id_department_id__exact=id_department_worker).filter(is_active=False)
        else:
            qs_worker = Worker.objects.none()
        return qs_worker.order_by('id').reverse()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name'] = _('Trabajadores en estado de baja ')
        context['title'] = _('Tabla de Trabajadores de baja')
        return context


class HeadDepartmentListView(BaseListView):
    model = HeadDepartment
    add_url = 'people/others/addheaddepartment/'
    update_url = 'people/others/updateheaddepartment/'

    def get(self, request, *args, **kwargs):
        try:
            is_person_user = request.user.person
        except:
            return redirect('/?next=%s' % request.path)
        else:
            if not request.user.has_perm('inventory.can_view_all_fixedasset'):
                raise PermissionDenied
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        person = cache.get('user_loger')
        return HeadDepartment.objects.filter(id_worker__id_department__id_area__exact=person['area']['id'])

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        page_size = self.get_paginate_by(self.get_queryset())
        if page_size:
            paginator, page, queryset, is_paginated = self.paginate_queryset(self.get_queryset(), page_size)
        # para crear un encabezado generico, pero añado al final una columna que no es un campo del modelo worker
        context['enc'] = [_('Nombre'), _('Nombre del Departamento'), _('Cantidad de Trabajadores')]
        context['page_obj'] = page
        context['hdpto'] = 'true'
        context['name'] = _('Jefes de Departamentos')
        context['title'] = _('Tabla de Departamentos')
        context['object_list'] = queryset
        return context


# ----------------ADD-----------------------------------------------------
class WorkerAddView(BaseAddView):
    model = Worker
    form_class = WorkerForm
    back_url = 'people/worker/'

    def get(self, request, *args, **kwargs):
        person = cache.get('user_loger')
        try:
            worker = get_object_or_404(Worker, id_person=person['id'])
        except:
            messages.error(self.request, _('Usted no es un Jefe de Departamento en el sistema'))
            return redirect('people:list_worker_view')
        if not request.user.has_perm('inventory.can_view_the_dpto_fixedasset') and not request.user.has_perm(
                'inventory.can_view_all_fixedasset'):
            raise PermissionDenied
        if request.user.has_perm('inventory.can_view_the_dpto_fixedasset'):
            self.form_class = HeadDepartmentWorkerForm
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, self.model._meta.verbose_name + _(' añadido exitosamente'))
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        if request.user.has_perm('inventory.can_view_the_dpto_fixedasset'):
            department = get_object_or_404(Worker,
                                           id_person__exact=request.user.person).id_department
            self.form_class = HeadDepartmentWorkerForm
            worker = request.POST.copy()
            worker['id_department'] = department
            form = HeadDepartmentWorkerForm(worker)
            if worker['is_active'] == 'on':
                is_active = True
            else:
                is_active = False
            if form.is_valid():
                worker = Worker(id_person=worker['id_person'], mail=worker['mail'],
                                id_department=worker['id_department'], is_active=is_active)
                worker.save()
                return redirect('people:list_worker_view')
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('people:list_worker_view')


class DepartmentAddView(BaseAddView):
    model = Department
    form_class = DepartmentForm
    back_url = 'people/others/department/'

    def get(self, request, *args, **kwargs):
        try:
            is_person_user = request.user.person
        except:
            return redirect('/?next=%s' % request.path)
        else:
            if not request.user.has_perm('inventory.can_view_the_dpto_fixedasset') and not request.user.has_perm(
                    'inventory.can_view_all_fixedasset') or request.user.has_perm(
                'inventory.can_view_the_dpto_fixedasset'):
                raise PermissionDenied
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        person = user_cache(self.request.user)
        new_form = form.data.copy()
        new_form['id_area'] = person['area']['id']
        dpto = Department(
            name=new_form['name'],
            id_area=new_form['id_area']
        )
        dpto.save()
        messages.success(self.request, self.model._meta.verbose_name + _(' añadido exitosamente'))
        return redirect('people:list_department_view')

    def get_success_url(self):
        return reverse('people:list_department_view')


class HeadDepartmentAddView(BaseAddView):
    model = HeadDepartment
    form_class = HeadDepartmentForm
    back_url = 'people/others/headdepartment/'

    def get(self, request, *args, **kwargs):
        try:
            is_person_user = request.user.person
        except:
            return redirect('/?next=%s' % request.path)
        else:
            if not request.user.has_perm('inventory.can_view_the_dpto_fixedasset') and not request.user.has_perm(
                    'inventory.can_view_all_fixedasset') or request.user.has_perm(
                'inventory.can_view_the_dpto_fixedasset'):
                raise PermissionDenied
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, self.model._meta.verbose_name + _(' añadido exitosamente'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('people:list_headdepartment_view')


# -----------------UPDATE--------------------------------------------------
class WorkerUpdateView(BaseUpdateView):
    model = Worker
    form_class = WorkerForm
    back_url = 'people/worker/'

    def get(self, request, *args, **kwargs):
        try:
            worker_user = get_object_or_404(Worker, id_person=request.user.person)
        except:
            return redirect('/?next=%s' % request.path)
        if not request.user.has_perm('inventory.can_view_the_dpto_fixedasset') and not request.user.has_perm(
                'inventory.can_view_all_fixedasset'):
            raise PermissionDenied
        if request.user.has_perm('inventory.can_view_the_dpto_fixedasset'):
            self.form_class = HeadDepartmentWorkerForm
            worker_seleted = get_object_or_404(Worker, id=int(kwargs['pk']))
            if worker_user.id_department.id != worker_seleted.id_department.id:
                raise PermissionDenied
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('people:list_worker_view')

    def get_form_class(self):
        if self.request.user.has_perm('inventory.can_view_the_dpto_fixedasset'):
            self.form_class = HeadDepartmentWorkerForm
        return super().get_form_class()


class DepartmentUpdateView(BaseUpdateView):
    model = Department
    form_class = DepartmentForm
    back_url = 'people/others/department'

    def get(self, request, *args, **kwargs):
        try:
            is_person_user = request.user.person
        except:
            return redirect('/?next=%s' % request.path)
        else:
            if not request.user.has_perm('inventory.can_view_the_dpto_fixedasset') and not request.user.has_perm(
                    'inventory.can_view_all_fixedasset') or request.user.has_perm(
                'inventory.can_view_the_dpto_fixedasset'):
                raise PermissionDenied
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('people:list_department_view')


class HeadDepartmentUpdateView(BaseUpdateView):
    model = HeadDepartment
    form_class = HeadDepartmentForm
    back_url = 'people/others/headdepartment/'

    def get(self, request, *args, **kwargs):
        try:
            is_person_user = request.user.person
        except:
            return redirect('/?next=%s' % request.path)
        else:
            if not request.user.has_perm('inventory.can_view_the_dpto_fixedasset') and not request.user.has_perm(
                    'inventory.can_view_all_fixedasset') or request.user.has_perm(
                'inventory.can_view_the_dpto_fixedasset'):
                raise PermissionDenied
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, self.model._meta.verbose_name + _(' añadido exitosamente'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('people:list_headdepartment_view')


# ---------------DELETE---------------------------------------------------
class DeleteWorkerView(DeleteBaseView):
    model = Worker
    success_url = reverse_lazy('people:list_worker_view')
    back_url = 'people/worker/'

    def get(self, request, *args, **kwargs):
        if not request.user.has_perm('inventory.can_view_the_dpto_fixedasset') and not request.user.has_perm(
                'inventory.can_view_all_fixedasset'):
            raise PermissionDenied
        context = self.context(request, args, kwargs)
        return render(request, 'crud_template/confirmation_delete.html', context)

    def qs(self, obj):
        return FixedAsset.objects.filter(id_worker__exact=obj.id)  # queryset de activos fijos de ese trabajador "obj"

    def remove(self, obj):
        qs = obj.fixedasset_set.all()  # devuelve un queryset de activos fijos que posean el worker "obj"
        if qs:
            messages.error(self.request, _('Solo puede dar baja a trabajadores sin activos fijos'))
            return False
        return True

    def message_delete(self, request):
        messages.success(request, _('Trabajadores eliminado exitosamente'))

    def check_persission(self, fixed_asset):
        worker_user = get_object_or_404(Worker, id_person=self.request.user.person)
        flag = False
        worker_object = get_object_or_404(Worker, id=fixed_asset)
        if self.request.user.has_perm(
                'inventory.can_view_all_fixedasset'):
            return True
        if self.request.user.has_perm('inventory.can_view_the_dpto_fixedasset'):
            if worker_object.id_department_id == worker_user.id_department_id:
                flag = True
        if not flag:
            return False  # si el activo fijo no pertenece al user en caso de ser user simple
            # o al departamento en caso de ser JD
        return True  # si puede ver el activo fijos


class DepartmentDeleteView(generic.DeleteView):
    model = Department
    template_name = 'crud_template/confirmation_delete.html'
    success_url = reverse_lazy('people:list_department_view')
    back_url = 'people/others/department/'

    def form_valid(self, form):
        messages.success(self.request, _('Departamento eliminado exitosamente'))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        name = socket.gethostname()
        ip = socket.gethostbyname(name)
        context['dpto'] = 'true'
        context['back_url'] = 'http://' + str(ip) + ':8000/' + str(self.back_url)
        return context

    def post(self, request, *args, **kwargs):
        dpto_obj = get_object_or_404(Department, id=int(kwargs['pk']))
        for w in dpto_obj.worker_set.all():
            for af in w.fixedasset_set.all():
                if af.id_worker.all().count() == 1:
                    af.is_active = False

                af.id_worker.remove(w)
                af.save()
        messages.success(request, _('Departamento eliminado exitosamente'))
        return super().post(request, *args, **kwargs)


# ----------------DETAIL--------------------------
class DetailWorkerView(DetaiBaseView):
    model = Worker

    def get(self, request, *args, **kwargs):
        try:
            worker_selected = get_object_or_404(Worker, id=int(kwargs['pk']))
        except:
            messages.error(request,
                           _('El ID : ' + str(kwargs['pk']) + ' no fue encontrado'))
            return redirect('people:list_worker_view')
        try:
            user_worker = get_object_or_404(Worker, id_person=request.user.person)
        except:
            return super().get(request, *args, **kwargs)
        else:
            if not request.user.has_perm('inventory.can_view_the_dpto_fixedasset') and not request.user.has_perm(
                    'inventory.can_view_all_fixedasset'):
                raise PermissionDenied
            if request.user.has_perm('inventory.can_view_the_dpto_fixedasset'):
                if worker_selected.id_department_id != user_worker.id_department_id:  # si pertenecen al mismo departamento
                    messages.error(request, _(
                        'El ID: ' + str(
                            worker_selected.id) + ' no pertenece al departamento ' + user_worker.id_department.name))
                    return redirect('people:list_worker_view')
            return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        body = []
        list_office = []
        qs_fixedasset = kwargs['object'].fixedasset_set.all()  # qs de activos fijos del worker seleccionado
        for fixedasset in qs_fixedasset:  # crear lista de oficinas de activos fijos del worker seleccionado
            if fixedasset.id_office not in list_office:
                list_office.append(fixedasset.id_office)
        for item in list_office:  # creando una extructura para pintar en la plantilla una tabla de activos fijos x cada oficina
            sub_list_fa = []
            for fixedasset in qs_fixedasset:
                if item.id == fixedasset.id_office.id:
                    sub_list_fa.append(fixedasset)
            body.append({
                'office': item,
                'list_fa': sub_list_fa
            })
            context['body'] = body
            context['office_all'] = Office.objects.all()
            if self.request.user.has_perm('inventory.can_view_all_fixedasset'):
                context['worker_all'] = Worker.objects.all()
            elif self.request.user.has_perm('inventory.can_view_the_dpto_fixedasset'):
                context['worker_all'] = Worker.objects.filter(id_department_id__exact=kwargs['object'].id_department.id)
        return context

    def post(self, request, *args, **kwargs):
        worker_detail = get_object_or_404(Worker, id=kwargs['pk'])
        for item in request.POST['list_id_office_worker'].split(','):
            try:
                fixed_asset = get_object_or_404(FixedAsset, id=int(item))
            except:
                messages.error(request, _('ID: ' + item) + ' no encontrado')
                return redirect('people:detail_worker_view', **kwargs)
            else:
                flag = True
                for worker in fixed_asset.id_worker.all():
                    if worker.id == worker_detail.id:
                        flag = False
                        break
                if (flag):  # si no encuentra al trabajador seleccionado entre los responsables del activos fijo
                    messages.error(request,
                                   _('El activo fijo No.Inv: ' + str(
                                       fixed_asset.stock_number) + ' no le pertenece al trabajador seleccionado'))
                    return redirect('people:detail_worker_view', **kwargs)
                if request.POST['type'] == 'oficina':
                    try:
                        office = get_object_or_404(Office, id=int(request.POST['select_modal']))
                    except:
                        messages.error(request, _(
                            'La oficina seleccionada no fue encontrada. ID: ' + str(request.POST['select_modal'])))
                        return redirect('people:detail_worker_view', **kwargs)
                    else:
                        fixed_asset.id_office = office
                        fixed_asset.save()
                        messages.success(request, _('Traslado realizado con exito'))
                elif request.POST['type'] == 'trabajador':
                    try:
                        worker_selected = get_object_or_404(Worker, id=int(request.POST['select_modal']))
                    except:
                        messages.error(request, _(
                            'El trabajador selccionado no fue encontrado. ID: ' + str(request.POST['select_modal'])))
                        return redirect('people:detail_worker_view', **kwargs)
                    else:
                        fixed_asset.id_worker.add(worker_selected)
                        fixed_asset.id_worker.remove(worker_detail)
                        messages.success(request, _('Traslado realizado con exito.'))
        return redirect('people:detail_worker_view', **kwargs)


class DetailUserView(View):
    model = Worker
    template_name = 'crud_template/detail.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/?next=%s' % request.path)
        try:
            worker = get_object_or_404(Worker, id_person=request.user.person)
        except:
            messages.error(self.request, _('Usted no es un trabajador en el sistema'))
            return redirect('inventory:list_fixed_asset_user_view')
        else:
            context = {
                'name': self.model._meta.verbose_name,
                'api_url': config('API_URL'),
                'object': worker
            }
            return render(request, self.template_name,
                          {'object': context['object'], 'name': context['name'], 'api_url': context['api_url'],
                           'true': True})

    def context(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name'] = self.model._meta.verbose_name
        context['api_url'] = config('API_URL')
        context['object'] = get_object_or_404(self.model, person=request.user.person)
        print(context['object'])
        print("context['object']")
        return context

    def object(self, request):
        object = get_object_or_404(self.model, person=request.user.person)
        return object
