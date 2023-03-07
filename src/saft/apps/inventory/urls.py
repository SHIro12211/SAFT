from django.urls import path

from .views import *

app_name = 'inventory'
urlpatterns = [
    path('filllocalstorage/', FillLocalStorage.as_view(), name='fill_local_storage'),
    path('home/', UserFixedAssetListView.as_view(), name='list_fixed_asset_user_view'),
    path('fixedasset/', FixedAssetListView.as_view(), name='list_fixed_asset_view'),
    path('fixedassetdisabled/', FixedAssetListDisabledView.as_view(), name='list_fixed_asset_disabled_view'),

    path('addfixedasset/', FixedAssetAddView.as_view(), name='add_fixed_asset_view'),

    path('updatefixedasset/<int:pk>/', FixedAssetUpdateView.as_view(), name='update_fixed_asset_view'),

    path('deletefixedasset/', DeleteFixetAssetView.as_view(), name='delete_fixed_asset_view'),
    path('detailfixedasset/<int:pk>/', DetailFixetAssetView.as_view(), name='detail_fixed_asset_view'),

    path('importpdf/', ExportPDF.as_view(), name='import_fixed_asset_to_pdf'),

    path('others/office/', OfficeListView.as_view(), name='list_office_view'),
    path('others/addoffice/', OfficeAddView.as_view(), name='add_office_view'),
    path('others/updateoffice/<int:pk>/', OfficeUpdateView.as_view(), name='update_office_view'),
    path('others/deleteoffice/<int:pk>/', OfficeDeleteeView.as_view(), name='delete_office_view'),

    path('others/typefixedasset/', TypeFixedAssetListView.as_view(), name='list_type_fixed_asset_view'),
    path('others/addtypefixedasset/', TypeFixedAsseAddView.as_view(), name='add_type_fixed_asset_view'),
    path('others/updatetypefixedasset/<int:pk>/', TypeFixedAsseUpdateView.as_view(), name='update_type_fixed_asset_view'),
    path('others/deletetypefixedasset/<int:pk>/', TypeFixedAsseDeleteeView.as_view(), name='delete_type_fixed_asset_view'),

]
