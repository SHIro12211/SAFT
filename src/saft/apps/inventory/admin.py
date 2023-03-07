from django.contrib import admin

from .form import FixedAssetForm, FixedAssetTypeForm, OfficeForm
from .models import FixedAsset, FixedAssetType, Office, FixedAssetStatu


# Register your models here.
class FixedAssetAdmin(admin.ModelAdmin):
    form = FixedAssetForm


class FixedAssetTypeAdmin(admin.ModelAdmin):
    form = FixedAssetTypeForm


class OfficeAdmin(admin.ModelAdmin):
    form = OfficeForm


admin.site.register(FixedAsset, FixedAssetAdmin)
admin.site.register(FixedAssetType, FixedAssetTypeAdmin)
admin.site.register(FixedAssetStatu)
admin.site.register(Office, OfficeAdmin)
