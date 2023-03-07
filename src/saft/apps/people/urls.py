from django.urls import path

from .views import *

app_name = 'people'
urlpatterns = [

    path('worker/', WorkerListView.as_view(), name='list_worker_view'),
    path('workerdisabled/', WorkerListDisabledView.as_view(), name='list_worker_disabled_view'),

    path('addworker/', WorkerAddView.as_view(), name='add_worker_view'),
    path('updateworker/<int:pk>/', WorkerUpdateView.as_view(), name='update_worker_view'),

    path('deleteworker/', DeleteWorkerView.as_view(), name='delete_worker_view'),

    path('detailworker/<int:pk>/', DetailWorkerView.as_view(), name='detail_worker_view'),
    path('detailuser/', DetailUserView.as_view(), name='detail_user_view'),
    path('others/adddepartment/', DepartmentAddView.as_view(), name='add_department_view'),
    path('others/department/', DepartmentListView.as_view(), name='list_department_view'),
    path('others/headdepartment/', HeadDepartmentListView.as_view(), name='list_headdepartment_view'),
    path('others/updatedepartment/<int:pk>/', DepartmentUpdateView.as_view(), name='update_department_view'),
    path('others/updateheaddepartment/<int:pk>/', HeadDepartmentUpdateView.as_view(),
         name='update_headdepartment_view'),
    path('others/addheaddepartment/', HeadDepartmentAddView.as_view(), name='add_headdepartment_view'),
    path('others/deletedepartment/<int:pk>/', DepartmentDeleteView.as_view(), name='delete_department_view'),

]
