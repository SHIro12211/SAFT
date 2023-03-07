import json
import socket

from decouple import config
from django.contrib import messages
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, get_object_or_404, render, get_list_or_404
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import generic, View

from saft.settings.base import GraphqlService
from .form import FixedAssetFilter, FixedAssetForm, FixedAssetFilterUser, FixedAssetFormSimpleuser, OfficeFilter, \
    OfficeForm, FixedAssetTypeForm, FixedAssetHeadDepartmentForm
from .models import FixedAsset, Office, FixedAssetType, FixedAssetStatu
from ..people.models import Worker, Department


# ------------------------------------------------------------------


class BaseListView(generic.ListView):  # clase generica de ListView
    template_name = 'crud_template/index.html'
    paginate_by = 12
    add_url = None
    update_url = None

    def get_all_field(self, value=0):  # devuelve una lista de campos del modelo desde el 'value' dado hasta el final
        ''':return devuelve una lista de los verbose_name del modelo'''
        list_res = []
        for item in self.model._meta.get_fields()[value:]:
            list_res.append(item.verbose_name)
        return list_res

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/?next=%s' % request.path)
        cache.set('user_loger', GraphqlService().get_person_by_id(request.user.person))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        name = socket.gethostname()
        ip = socket.gethostbyname(name)
        context['add_url'] = 'http://' + str(ip) + ':8000/' + self.add_url
        context['update_url'] = 'http://' + str(ip) + ':8000/' + self.update_url
        context['api_url'] = config('API_URL')
        return context


class FixedAssetListView(BaseListView):
    model = FixedAsset
    add_url = 'inventory/addfixedasset/'
    update_url = 'inventory/updatefixedasset/'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        # clase filtro del django-filter que recibe una solicitud GET y el queryset que deseas filtrar
        f = FixedAssetFilter(self.request.GET, self.get_queryset())
        # paginar el queryset por parametro, o sea el queryset del django-filter recibido
        page_size = self.get_paginate_by(f)
        queryset = None
        if page_size:
            paginator, page, queryset, is_paginated = self.paginate_queryset(f.qs, page_size)
        context['enc'] = self.get_all_field(1)[:7]
        context['filter'] = f
        context['title'] = _('Tabla de Activos Fijos')
        person = cache.get('user_loger')
        if self.request.user.has_perm('inventory.can_view_all_fixedasset'):
            var = _(str(person['area']['name']))
        if self.request.user.has_perm('inventory.can_view_the_dpto_fixedasset'):
            try:
                dpto_name = get_object_or_404(Worker, id_person=self.request.user.person).id_department.name
            except:
                var = 'Departamento'
            else:
                var = _(str(dpto_name))
        else:
            var = ''

        qs_office = Office.objects.filter(
            fixedasset__id_worker__id_department__id_area__exact=int(person['area']['id'])).distinct()
        context['name'] = _('Activos Fijos de ') + var
        context['af'] = 'true'
        context['page_obj'] = page
        context['object_list'] = queryset
        context['office_list'] = qs_office
        return context

    def get_queryset(self):
        if self.request.user.has_perm('inventory.can_view_all_fixedasset'):  # si el user es un Jefe de Area
            person = cache.get('user_loger')
            qs_fixed_asset = FixedAsset.objects.filter(
                id_worker__id_department__id_area__exact=int(person['area']['id'])).filter(is_active=True).distinct()
        elif self.request.user.has_perm('inventory.can_view_the_dpto_fixedasset'):  # si es Jefe de Dpto
            # id del departamento del user auntentificado en el sistema
            try:
                id_department_worker = get_object_or_404(Worker,
                                                         id_person__exact=self.request.user.person).id_department.id
            except:
                messages.error(self.request, _('Usted no es un Jefe de Departamento en el sistema'))
                return FixedAsset.objects.none()
            else:
                # obtener solo el id del departamento del trabajador autentificado
                qs_fixed_asset = FixedAsset.objects.filter(id_worker__id_department__exact=id_department_worker) \
                    .distinct().filter(is_active=True)
                # qs de activos fijos  del departamento del trabajador autentificado
        else:
            raise PermissionDenied
        return qs_fixed_asset.order_by('id').reverse()


class UserFixedAssetListView(FixedAssetListView):  # vista para mostrar los activos fijos del user

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        f = FixedAssetFilterUser(self.request.GET, self.get_queryset())
        person = cache.get('user_loger')
        qs_office = Office.objects.filter(
            fixedasset__id_worker__id_person__exact=int(person['id'])).distinct()
        context['filter'] = f
        context['name'] = _('Mis Activos Fijos')
        context['office_list'] = qs_office
        return context

    def get_queryset(self):
        return FixedAsset.objects.filter(id_worker__id_person__exact=self.request.user.person).filter(
            is_active=True).order_by('id').reverse()


class FixedAssetListDisabledView(FixedAssetListView):  # vista para mostrar los activos fijos desactivados

    def get(self, request, *args, **kwargs):
        if not request.user.has_perm('inventory.can_view_the_dpto_fixedasset') and not request.user.has_perm(
                'inventory.can_view_all_fixedasset'):
            messages.error(request, _('Usted no tiene persmiso para acceder a esa vista'))
            raise PermissionDenied
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name'] = _('Activos Fijos en estado de baja')
        return context

    def get_queryset(self):
        person = cache.get('user_loger')
        return FixedAsset.objects.filter(id_office__id_area__exact=int(person['area']['id'])).filter(is_active=False)


class OfficeListView(BaseListView):
    model = Office
    add_url = 'inventory/others/addoffice/'
    update_url = 'inventory/others/updateoffice/'

    def get_queryset(self):
        person = cache.get('user_loger')
        if not self.request.user.has_perm('inventory.can_view_the_dpto_fixedasset') and not self.request.user.has_perm(
                'inventory.can_view_all_fixedasset'):
            raise PermissionDenied
        if self.request.user.has_perm('inventory.can_view_the_dpto_fixedasset') or self.request.user.has_perm(
                'inventory.can_view_all_fixedasset'):
            return Office.objects.filter(id_area__exact=int(person['area']['id'])).distinct().order_by(
                'id').reverse()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        # clase filtro del django-filter que recibe una solicitud GET y el queryset que deseas filtrar
        f = OfficeFilter(self.request.GET, self.get_queryset())
        page_size = self.get_paginate_by(f)
        queryset = None
        if page_size:
            paginator, page, queryset, is_paginated = self.paginate_queryset(f.qs, page_size)
        if self.request.user.has_perm('inventory.can_view_the_dpto_fixedasset'):
            try:
                worker_user = get_object_or_404(Worker, id_person=self.request.user.person)
            except:
                var = ''
            else:
                var = 'Oficinas con activos fijos del departamento de ' + str(
                    get_object_or_404(Department, id=worker_user.id_department.id).name)
        if self.request.user.has_perm('inventory.can_view_all_fixedasset'):
            var = _('Oficinas del Área')
        context['enc'] = [_('Número'), _('cantidad de activos fijos'), _('Descripción')]
        context['title'] = _('Tabla de Oficinas')
        context['filter'] = f
        context['name'] = var
        context['offi'] = 'true'
        context['page_obj'] = page
        context['object_list'] = queryset
        context['api_url'] = config('API_URL')
        return context


class TypeFixedAssetListView(BaseListView):
    model = FixedAssetType
    template_name = 'crud_template/index.html'
    add_url = 'inventory/others/addtypefixedasset/'
    update_url = 'inventory/others/updatetypefixedasset/'

    def get(self, request, *args, **kwargs):
        if not request.user.has_perm('inventory.can_view_the_dpto_fixedasset') and not request.user.has_perm(
                'inventory.can_view_all_fixedasset'):
            messages.error(request, _('Usted no tiene persmiso para acceder a esa vista'))
            raise PermissionDenied
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        person = cache.get('user_loger')
        return FixedAssetType.objects.filter(
            fixedasset__id_worker__id_department__id_area__exact=int(person['area']['id'])).order_by(
            'id').reverse().distinct()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        person = cache.get('user_loger')
        list_type = []
        qs_type_fixed_asset = FixedAssetType.objects.filter(
            fixedasset__id_worker__id_department__id_area__exact=int(person['area']['id'])).distinct()
        for qs in self.get_queryset():
            count = 0
            for qs2 in qs_type_fixed_asset:
                print('s')
                if qs2.type_FixedAsset == qs.type_FixedAsset:
                    count = count + 1
            list_type.append({
                'qs': qs,
                'count': count
            })
        context['enc'] = [_('Tipo'), _('Cantidad de activos fijos')]
        context['title'] = _('Tabla de Tipos de Activos Fijos')
        context['name'] = _('Tipos de Activos Fijos del Área')
        context['type_fa'] = 'true'
        context['object_list'] = list_type
        return context


# -----------ADD---------------------

class BaseAddView(generic.CreateView):
    template_name = 'crud_template/add_edit.html'
    back_url = None

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/?next=%s' % request.path)
        cache.set('user_loger', GraphqlService().get_person_by_id(request.user.person))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        name = socket.gethostname()
        ip = socket.gethostbyname(name)
        context['back'] = 'http://' + str(ip) + ':8000/' + self.back_url
        context['name'] = _('Añadir ') + self.model._meta.verbose_name
        context['api_url'] = config('API_URL')
        return context

    def post(self, request, *args, **kwargs):
        cache.set('user_loger', GraphqlService().get_person_by_id(request.user.person))
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, self.model._meta.verbose_name + _(' añadido exitosamente'))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _('Datos incorrectos, por favor, corriga los errores señalados'))
        return super().form_invalid(form)


class FixedAssetAddView(BaseAddView):
    model = FixedAsset
    form_class = FixedAssetForm
    back_url = 'inventory/home/'

    def get(self, request, *args, **kwargs):
        if not request.user.has_perm('inventory.can_view_the_dpto_fixedasset') and not request.user.has_perm(
                'inventory.can_view_all_fixedasset'):
            self.form_class = FixedAssetFormSimpleuser
        if request.user.has_perm('inventory.can_view_the_dpto_fixedasset'):
            self.form_class = FixedAssetHeadDepartmentForm
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('inventory:list_fixed_asset_user_view')

    def post(self, request, *args, **kwargs):
        data = request.POST.copy()
        if request.user.has_perm('inventory.can_view_the_dpto_fixedasset'):
            self.form_class = FixedAssetHeadDepartmentForm
        if not request.user.has_perm('inventory.can_view_the_dpto_fixedasset') and not request.user.has_perm(
                'inventory.can_view_all_fixedasset'):
            try:
                worker = get_object_or_404(Worker, id_person=request.user.person)  # objeto del user auntentificado
            except:
                messages.error(request, _(
                    'Usted no es un trabajador de esta área aun. Consulte a su Jefe de Área o de Departamento para añadirlo al sistema'))
                return redirect('inventory:list_fixed_asset_user_view')
            else:
                self.form_class = FixedAssetFormSimpleuser
                form = FixedAssetFormSimpleuser(data)
                try:
                    # intenta imprimir en consola el dato data['id_worker'], dato que nunca debe imprimirse,
                    # en caso de que se imprima, mando un message.error o en caso de error(q es lo mas comun)
                    # el formulacio se trabaja de forma normal segun el user
                    print('El user loco este quiere modificar el HTML a nivel noob' + data['id_worker'])
                    messages.error(request, _('El usario actual no tiene permiso para realizar la operacion anterior'))
                    return redirect('inventory:add_fixed_asset_view')
                except:
                    try:
                        type_fixed_asset = get_object_or_404(FixedAssetType, id=data['id_fixed_asset_type'])
                        fixed_asset_statu = get_object_or_404(FixedAssetStatu, id=data['id_statu'])
                        office = get_object_or_404(Office, id=data['id_office'])
                    except:
                        return super().post(request, *args, **kwargs)
                    if form.is_valid():
                        fixedasset = FixedAsset(
                            stock_number=data['stock_number'],
                            id_fixed_asset_type=type_fixed_asset,
                            model=data['model'],
                            brand=data['brand'],
                            serial_number=data['serial_number'],
                            id_statu=fixed_asset_statu,
                            id_office=office,
                            observations=data['observations'],
                            is_active=True,
                        )
                        fixedasset.save()
                        fixedasset.id_worker.add(worker)
                        return redirect('inventory:list_fixed_asset_user_view')
                    else:
                        return super().post(request, *args, **kwargs)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        print('llego')
        worker = get_object_or_404(Worker, id_person=self.request.user.person)  # user logeado
        flag = False
        if self.request.user.has_perm('inventory.can_view_all_fixedasset'):
            id_select = form.data['id_office']
            list_office_the_area = get_list_or_404(Office, id_area=worker.id_department.id_area)
            for w in list_office_the_area:
                if w.id == int(id_select):
                    flag = True
                    break
            try:
                id_select = form.data['id_worker']
            except:
                form.add_error('id_worker', _("Este campo es obligatorio"))
                return self.form_invalid(form)
            if not flag:  # si no existe el trabajador en el departamento del user logeado
                form.add_error('id_office',
                               'Escoja una opción válida. ' + id_select + ' no es una de las opciones disponibles.')
                return self.form_invalid(form)
        if self.request.user.has_perm('inventory.can_view_the_dpto_fixedasset'):
            try:
                id_select = form.data['id_worker']
            except:
                form.add_error('id_worker', _("Este campo es obligatorio"))
                return self.form_invalid(form)
            else:
                list_workers_same_dpto = get_list_or_404(Worker, id_department_id=worker.id_department_id)
                for w in list_workers_same_dpto:
                    if w.id == int(id_select):
                        flag = True
                        break
                if not flag:  # si no existe el trabajador en el departamento del user logeado
                    form.add_error('id_worker',
                                   'Escoja una opción válida. ' + id_select + ' no es una de las opciones disponibles.')
                    return self.form_invalid(form)
        return super().form_valid(form)

    def form_invalid(self, form):
        try:
            id_select = form.data['id_worker']
        except:
            form.add_error('id_worker', _("Este campo es obligatorio"))
            return super().form_invalid(form)


class OfficeAddView(BaseAddView):
    model = Office
    back_url = 'inventory/others/office/'
    form_class = OfficeForm

    def get(self, request, *args, **kwargs):
        if not request.user.has_perm('inventory.can_view_the_dpto_fixedasset') and not request.user.has_perm(
                'inventory.can_view_all_fixedasset'):
            raise PermissionDenied
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('inventory:list_office_view')

    def form_valid(self, form):
        person = cache.get('user_loger')
        new_form = form.data.copy()
        print(new_form)
        new_form['id_area'] = person['area']['id']
        print(new_form['id_area'])
        office = Office(
            number=new_form['number'],
            id_area=new_form['id_area'],
            description=new_form['description']
        )
        office.save()
        messages.success(self.request, self.model._meta.verbose_name + _(' añadido exitosamente'))
        return redirect('inventory:list_office_view')


class TypeFixedAsseAddView(BaseAddView):
    model = FixedAssetType
    form_class = FixedAssetTypeForm
    template_name = 'crud_template/add_edit.html'
    back_url = 'inventory/others/typefixedasset/'

    def get(self, request, *args, **kwargs):
        if not request.user.has_perm('inventory.can_view_the_dpto_fixedasset') and not request.user.has_perm(
                'inventory.can_view_all_fixedasset'):
            messages.error(request, _('Usted no tiene persmiso para acceder a esa vista'))
            raise PermissionDenied
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('inventory:list_type_fixed_asset_view')


# !-------------Update------------------

class BaseUpdateView(generic.UpdateView):
    template_name = 'crud_template/add_edit.html'
    back_url = None

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/?next=%s' % request.path)
        cache.set('user_loger', GraphqlService().get_person_by_id(request.user.person))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        name = socket.gethostname()
        ip = socket.gethostbyname(name)
        context['back'] = 'http://' + str(ip) + ':8000/' + self.back_url
        context['name'] = _('Editar ') + self.model._meta.verbose_name
        context['flag'] = 'true'
        context['api_url'] = config('API_URL')
        return context

    def post(self, request, *args, **kwargs):
        cache.set('user_loger', GraphqlService().get_person_by_id(request.user.person))
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, self.model._meta.verbose_name + _(' editado exitosamente'))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _('Datos incorrectos, por favor, corriga los errores señalados'))
        return super().form_invalid(form)


class FixedAssetUpdateView(BaseUpdateView):
    model = FixedAsset
    form_class = FixedAssetForm
    back_url = 'inventory/home/'

    def get(self, request, *args, **kwargs):
        try:
            worker_user = get_object_or_404(Worker, id_person=request.user.person)
        except:
            messages.error(request, _("Usted no es un trabajador del sistema"))
            return redirect('/?next=%s' % request.path)
        if not request.user.has_perm('inventory.can_view_the_dpto_fixedasset') and not request.user.has_perm(
                'inventory.can_view_all_fixedasset'):
            self.form_class = FixedAssetFormSimpleuser
            for fixedasset in worker_user.fixedasset_set.all():
                if fixedasset.id == int(kwargs['pk']):
                    return super().get(request, *args, **kwargs)
            messages.error(request, _('El activo fijo ID:' + str(kwargs['pk']) + 'no le pertenece'))
            return redirect(
                'inventory:list_fixed_asset_user_view')  # si termino el for sin encontrar niguna similitud, la vista levanta un error 403
        if request.user.has_perm('inventory.can_view_the_dpto_fixedasset'):
            self.form_class = FixedAssetHeadDepartmentForm
            try:
                fixedasset_obj = get_object_or_404(FixedAsset, id=int(kwargs['pk']))
            except:
                messages.error(request, _('El activo fijo ID:' + str(kwargs['pk']) + ' no fue encontrado'))
                return redirect('inventory:list_fixed_asset_user_view')
            for worker in fixedasset_obj.id_worker.all().select_related('id_department'):
                if worker.id_department.id == worker_user.id_department.id:
                    return super().get(request, *args, **kwargs)
            messages.error(request, _('El activo fijo ID:' + str(
                fixedasset_obj.id) + ' no pertenece a un trabajador del departamanto ' + worker_user.id_department.name))
            return redirect('inventory:list_fixed_asset_user_view')
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('inventory:list_fixed_asset_user_view')

    def post(self, request, *args, **kwargs):
        if not request.user.has_perm('inventory.can_view_the_dpto_fixedasset') and not request.user.has_perm(
                'inventory.can_view_all_fixedasset'):
            self.form_class = FixedAssetFormSimpleuser
        if request.user.has_perm('inventory.can_view_the_dpto_fixedasset'):
            self.form_class = FixedAssetHeadDepartmentForm
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        worker = get_object_or_404(Worker, id_person=self.request.user.person)  # user logeado
        flag = False
        if self.request.user.has_perm('inventory.can_view_the_dpto_fixedasset'):
            try:
                id_select = form.data['id_worker']
            except:
                form.add_error('id_worker',
                               'Este campo es obligatorio.')
                return self.form_invalid(form)
            list_workers_same_dpto = get_list_or_404(Worker, id_department_id=worker.id_department_id)
            for w in list_workers_same_dpto:
                if w.id == int(id_select):
                    flag = True
                    break
            if not flag:  # si no existe el trabajador en el departamento del user logeado
                form.add_error('id_worker',
                               'Escoja una opción válida. ' + id_select + ' no es una de las opciones disponibles.')
                return self.form_invalid(form)
        return super().form_valid(form)


class OfficeUpdateView(BaseUpdateView):
    model = Office
    back_url = 'inventory/others/office/'
    form_class = OfficeForm

    def get(self, request, *args, **kwargs):
        if not request.user.has_perm('inventory.can_view_the_dpto_fixedasset') and not request.user.has_perm(
                'inventory.can_view_all_fixedasset'):
            raise PermissionDenied
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('inventory:list_office_view')


class TypeFixedAsseUpdateView(BaseUpdateView):
    model = FixedAssetType
    form_class = FixedAssetTypeForm
    template_name = 'crud_template/add_edit.html'
    back_url = 'inventory/others/typefixedasset/'

    def get(self, request, *args, **kwargs):
        try:
            worker_user = get_object_or_404(Worker, id_person=request.user.person)
        except:
            return redirect('/?next=%s' % request.path)
        if not request.user.has_perm('inventory.can_view_the_dpto_fixedasset') and not request.user.has_perm(
                'inventory.can_view_all_fixedasset'):
            messages.error(request, _('Usted no tiene persmiso para acceder a esa vista'))
            raise PermissionDenied
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('inventory:list_type_fixed_asset_view')


# -----------Eliminar-----------------------

class DeleteBaseView(View):  # clase base de elminar masivo e individual
    model = None
    success_url = None
    back_url = None

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/?next=%s' % request.path)
        cache.set('user_loger', GraphqlService().get_person_by_id(request.user.person))
        return super().get(request, *args, **kwargs)

    def context(self, request, *args, **kwargs):  # cuando renderiza la ventana de confirmacion
        # parameter lista de id de modelos que desea desactivar
        list_object_delete = []
        id_error_404 = ''
        id_error_403 = ''
        for id in request.GET['list_id'].split(','):  # dividir la cadena de texto de id y recorrerla
            try:
                object_model = get_object_or_404(self.model, id=int(id))  # devulve el modelo con este id "id"
            except:
                id_error_404 += id + ', '  # string de id que no existen
            else:
                # devulve un queryset de la sublista relacionada con ese modelo a desactivar
                if not self.check_persission(int(id)):  # si no se puede ver el activo fijo
                    id_error_403 += id + ', '
                    continue
                qs_fa_w = self.qs(object_model)
                if qs_fa_w:
                    list_sub = []
                    for elem in qs_fa_w:
                        list_sub.append(elem)
                    # lista de diccionarios donde tiene un modelo a desactivar y una sublist relacionada a el
                    list_object_delete.append({'obj_delete': object_model, 'list': list_sub})
                else:
                    # lista de diccionarios donde solo tiene un modelo a desactivar
                    list_object_delete.append({'obj_delete': object_model})
        '''diccionario que muestra lista de objetos a desactivar y su sublista, 
        una bandera que idnetificara si es una eliminacion masiva o individual y 
        la cadena de texto que contiene los id de los modelos a desactivar para su uso en el metodo post'''
        if len(id_error_404) > 0:
            messages.error(request, 'ID no encontrados :' + id_error_404[:len(id_error_404) - 2])
        if len(id_error_403) > 0:
            if request.user.has_perm('inventory.can_view_the_dpto_fixedasset'):
                messages.error(request,
                               'Los siguientes ID: ' + id_error_403[
                                                       :len(id_error_403) - 2] + ' no pertenecen a su departamanto ')
            else:
                messages.error(request,
                               'Los siguientes ID: ' + id_error_403[
                                                       :len(id_error_403) - 2] + ' no pertenecen')
        context = {'list_object': list_object_delete, "list_id": request.GET['list_id']}
        name = socket.gethostname()
        ip = socket.gethostbyname(name)
        context['api_url'] = config('API_URL')
        context['back_url'] = 'http://' + str(ip) + ':8000/' + str(self.back_url)
        return context

    def post(self, request, *args, **kwargs):
        list_delete = []
        for item_id in request.POST['list_object_delete'].split(','):
            obj = get_object_or_404(self.model, id=int(item_id))  # objeto del modelo que voy a desactivar
            if self.remove(obj):
                obj.is_active = False
                obj.save()
                list_delete.append(obj)
            else:
                messages.error(request, _('Solo puede dar baja a trabajadores que no posean activos fijos'))
                return redirect('people:list_worker_view')
        self.message_delete(request)
        return HttpResponseRedirect(self.success_url)


class DeleteFixetAssetView(DeleteBaseView):
    model = FixedAsset
    success_url = reverse_lazy('inventory:list_fixed_asset_user_view')
    back_url = 'inventory/home/'

    def get(self, request, *args, **kwargs):
        context = self.context(request, args, kwargs)
        context['flag'] = 'true'

        return render(request, 'crud_template/confirmation_delete.html', context)

    def qs(self, obj):
        return obj.id_worker.all()  # devuelve todos los trabajadores que posean ese activo fijo "obj"

    def remove(self, obj):
        obj.id_worker.clear()  # elimina toda relación con el mododelo a desactivar
        return True

    def message_delete(self, request):
        messages.success(request, _('Activo fijo eliminado exitosamente'))

    def check_persission(self, fixed_asset):
        worker_user = get_object_or_404(Worker, id_person=self.request.user.person)
        flag = False
        person = cache.get('user_loger')
        fixedasset_object = get_object_or_404(FixedAsset, id=fixed_asset)
        if self.request.user.has_perm(
                'inventory.can_view_all_fixedasset'):
            if fixedasset_object.id_office.id_area == int(person['area']['id']):
                return True
            else:
                return False
        for worker in fixedasset_object.id_worker.all():
            if not self.request.user.has_perm(
                    'inventory.can_view_the_dpto_fixedasset') and not self.request.user.has_perm(
                'inventory.can_view_all_fixedasset'):
                if worker.id == worker_user.id:
                    flag = True
                    break
            if self.request.user.has_perm('inventory.can_view_the_dpto_fixedasset'):
                if worker.id_department_id == worker_user.id_department_id:
                    flag = True
                    break
        if not flag:
            return False  # si el activo fijo no pertenece al user en caso de ser user simple
            # o al departamento en caso de ser JD
        return True  # si puede ver el activo fijos


class OfficeDeleteeView(generic.DeleteView):
    model = Office
    back_url = 'inventory/others/office/'
    template_name = 'crud_template/confirmation_delete.html'

    def get(self, request, *args, **kwargs):
        try:
            worker_user = get_object_or_404(Worker, id_person=request.user.person)
        except:
            return redirect('/?next=%s' % request.path)
        if not request.user.has_perm('inventory.can_view_the_dpto_fixedasset') and not request.user.has_perm(
                'inventory.can_view_all_fixedasset'):
            messages.error(request, _('Usted no tiene persmiso para acceder a esa vista'))
            raise PermissionDenied
        cache.set('user_loger', GraphqlService().get_person_by_id(request.user.person))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        name = socket.gethostname()
        ip = socket.gethostbyname(name)
        context['back_url'] = 'http://' + str(ip) + ':8000/' + self.back_url
        context['offi'] = 'true'
        context['api_url'] = config('API_URL')
        return context

    def get_success_url(self):
        return reverse('inventory:list_office_view')

    def form_valid(self, form):
        messages.success(self.request, _('Oficina eliminada exitomante'))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _('Datos incorrectos, por favor, corriga los errores señalados'))
        return super().form_invalid(form)


class TypeFixedAsseDeleteeView(generic.DeleteView):
    model = FixedAssetType
    back_url = 'inventory/others/typefixedasset/'
    template_name = 'crud_template/confirmation_delete.html'

    def get(self, request, *args, **kwargs):
        try:
            worker_user = get_object_or_404(Worker, id_person=request.user.person)
        except:
            return redirect('/?next=%s' % request.path)
        if not request.user.has_perm('inventory.can_view_the_dpto_fixedasset') and not request.user.has_perm(
                'inventory.can_view_all_fixedasset'):
            messages.error(request, _('Usted no tiene persmiso para acceder a esa vista'))
            raise PermissionDenied
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        name = socket.gethostname()
        ip = socket.gethostbyname(name)
        context['back_url'] = 'http://' + str(ip) + ':8000/' + self.back_url
        context['type_fa'] = 'true'
        context['api_url'] = config('API_URL')
        return context

    def get_success_url(self):
        return reverse('inventory:list_type_fixed_asset_view')

    def post(self, request, *args, **kwargs):
        messages.success(self.request, _('Tipo de activo fijo eliminado exitomante'))
        return super().post(request, *args, **kwargs)


# -------------DETAIL--------------------------------
class DetaiBaseView(generic.DetailView):
    template_name = 'crud_template/detail.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/?next=%s' % request.path)
        cache.set('user_loger', GraphqlService().get_person_by_id(request.user.person))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name'] = _('Detalles de ') + self.model._meta.verbose_name
        context['api_url'] = config('API_URL')
        return context


class DetailFixetAssetView(DetaiBaseView):
    model = FixedAsset

    def get(self, request, *args, **kwargs):
        get = super().get(request, *args, **kwargs)
        person = cache.get('user_loger')
        try:
            fixedasset_selected = get_object_or_404(FixedAsset, id=int(kwargs['pk']))
        except:
            messages.error(request, _('El activo fijo ID:' + str(kwargs['pk']) + ' no fue encontrado'))
            return redirect('inventory:list_fixed_asset_user_view')
        user_worker = get_object_or_404(Worker, id_person=request.user.person)
        if not request.user.has_perm('inventory.can_view_the_dpto_fixedasset') and not request.user.has_perm(
                'inventory.can_view_all_fixedasset'):
            for fixedasset in user_worker.fixedasset_set.all():
                if fixedasset.id == fixedasset_selected.id:  # si el worker logeado tiene el activo fijo
                    return super().get(request, *args, **kwargs)
            messages.error(request, _('El activo fijo ID:' + str(fixedasset_selected.id) + 'no le pertenece'))
            return redirect('inventory:list_fixed_asset_user_view')
        if request.user.has_perm('inventory.can_view_the_dpto_fixedasset'):
            for worker in fixedasset_selected.id_worker.all().select_related('id_department'):
                if worker.id_department_id == user_worker.id_department_id:  # si pertenecen al mismo departamento
                    return super().get(request, *args, **kwargs)
            messages.error(request, _('El activo fijo ID:' + str(
                fixedasset_selected.id) + ' no pertenece a un trabajador del departamanto ' + user_worker.id_department.name))
            return redirect('inventory:list_fixed_asset_user_view')
        if request.user.has_perm('inventory.can_view_all_fixedasset'):
            if fixedasset_selected.id_office.id_area == int(person['area']['id']):
                return get
            else:
                messages.error(request, _('El activo fijo ID:' + str(
                    fixedasset_selected.id) + ' no pertenece a un trabajador del Área de ' + str(
                    person['area']['name'])))
                return redirect('inventory:list_fixed_asset_user_view')
        return get


# !-----------Import PDF---------------------
class ExportPDF(View):
    model = FixedAsset

    def get(self, request, *args, **kwargs):
        person = cache.get('user_loger')
        qs_office = Office.objects.filter(fixedasset__id_worker__id_person__exact=request.user.person).filter(
            id_area__exact=int(person['area']['id'])).distinct()
        context = {'office': qs_office, 'title': 'Seleccione una oficina para importar',
                   'name': _('Exportar activos fijos a PDF')}
        messages.info(request, _('Seleccione una oficina para exportar sus activos fijos'))
        cache.set('user_loger', GraphqlService().get_person_by_id(request.user.person))
        return render(request, 'export_pdf.html', context)

    def post(self, request):
        qs_office = Office.objects.filter(fixedasset__id_worker__id_person__exact=request.user.person).distinct()
        worker = get_object_or_404(Worker, id_person=request.user.person).id_person
        enc = ['No', _('Número de inventario'), _('Tipo'), _('Modelo'), _('Marca'), _('Número de serie'), _('Estado'),
               _('Responsable(s)'), _('Observaciones')]
        area = GraphqlService().get_person_by_id(request.user.person)['area']['name']

        qs_fixedassent = FixedAsset.objects.filter(id_office__id__exact=request.POST['select_office']).filter(
            id_worker__id_person__exact=request.user.person)
        selected_office = Office.objects.get(id=request.POST['select_office'])
        struct_responsible = []
        for fa in qs_fixedassent:
            list_responsible = []
            for w in fa.id_worker.all():
                graph = GraphqlService().get_person_by_id(w.id_person)
                if graph:
                    # name_list = graph['name'].split(' ')
                    # name_list.pop(len(name_list) - 1)
                    # name_short = ' '.join(name_list)
                    # lo comentado es para eliminar el 2do apellido
                    list_responsible.append(graph['name'])
            struct_responsible.append({
                'id': fa.id,
                'list_responsible': list_responsible
            })
        list_responsible_signature = []
        for fa in qs_fixedassent:
            for w in fa.id_worker.all():
                name_responsible = GraphqlService().get_person_by_id(w.id_person)['name']
                if name_responsible not in list_responsible_signature:
                    list_responsible_signature.append(name_responsible)
        context = {
            'worker': worker,
            'fixedassent': qs_fixedassent,
            'dic_responsbile': struct_responsible,
            'enc': enc,
            'area': area,
            'office_selected': selected_office,
            'office': qs_office,
            'title': "Exportar Activos Fijos",
            'name': _('Exportar activos fijos a PDF'),
            'responsible_signature': list_responsible_signature,
            'api_url': config('API_URL')}
        return render(request, 'export_pdf.html', context)


class FillLocalStorage(generic.View):
    def post(self, request, *args, **kwargs):
        res = json.loads(request.body)
        list_dic = []
        person = cache.get('user_loger')
        grapfh_data = GraphqlService().get_all_person_for_area(person['area']['name'])
        if request.user.has_perm('inventory.can_view_all_fixedasset'):
            qs_worker = Worker.objects.filter(id_department__id_area__exact=int(person['area']['id'])).only('id_person')
            print(qs_worker)
        elif request.user.has_perm('inventory.can_view_the_dpto_fixedasset'):
            dpto_id = get_object_or_404(Worker, id_person=res['user']).id_department.id
            qs_worker = Worker.objects.filter(id_department_id__exact=dpto_id).only('id_person')
        else:
            qs_worker = Worker.objects.filter(id_person__exact=res['user'])
        for worker_id in qs_worker:
            active = True
            for grapfh in grapfh_data:
                if str(worker_id.id_person) == str(grapfh['id']):
                    if grapfh['isActive'] == False:
                        active = False
                    list_dic.append({
                        'id': grapfh['id'],
                        'name': grapfh['name'],
                        'area': True,
                        'active': active
                    })
        data = {'data': list_dic}
        print(data)
        return JsonResponse(data, status=200)
