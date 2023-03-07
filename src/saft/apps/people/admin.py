from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.cache import cache
from django.urls import path

from saft.settings.base import GraphqlService
from .form import UserChangeMixinForm, UserCreationMixinForm, HeadAreaForm, WorkerFormAdmin
from .models import User, Department, Worker, HeadDepartment, HeadArea
# Register your models here.
from .views import PersonAutocompleteView, IdAreaAutocompleteView


class UserAdmin(BaseUserAdmin):
    form = UserChangeMixinForm
    add_form = UserCreationMixinForm
    list_display = ("username", "email", "is_active", "is_staff")
    add_fieldsets = (
        (None,
         {
             "classes": ('wide',),
             "fields": ('username', 'password1', 'password2', 'person'),
         },
         ),
    )
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('person',)}),
        (("Permissions"),
         {
             "fields": (
                 "is_active",
                 "is_staff",
                 "groups",
                 "user_permissions",
             ),
         },
         ),
    )

    def __init__(self, model, Adminsite):
        cache.set('all_person', GraphqlService().get_all_person_to_choice())
        return super().__init__(model, Adminsite)

    def get_urls(self):
        return [
                   path('personcomplete/', self.admin_site.admin_view(PersonAutocompleteView.as_view()),
                        name='people_user_personcomplete'),
                   path('id_areancomplete/', self.admin_site.admin_view(IdAreaAutocompleteView.as_view()),
                        name='people_head_area_personcomplete')
               ] + super().get_urls()


# !-----------------------------------------
class WorkerAdmin(admin.ModelAdmin):
    form = WorkerFormAdmin
    list_filter = ["id_department", "is_active"]


class HeadAreaAdmin(admin.ModelAdmin):
    form = HeadAreaForm


# !-----------------------------------------
admin.site.register(User, UserAdmin)
admin.site.register(Worker, WorkerAdmin)
admin.site.register(Department)
admin.site.register(HeadDepartment)
admin.site.register(HeadArea, HeadAreaAdmin)
