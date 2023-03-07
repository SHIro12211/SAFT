from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include
from django.utils.translation import gettext_lazy as _
from saft.apps.people.form import MyLoginForm

urlpatterns = [

    path('inventory/', include('saft.apps.inventory.urls')),
    path('people/', include('saft.apps.people.urls')),
    path(_('admin/'), admin.site.urls),

    path('', LoginView.as_view(form_class=MyLoginForm, template_name="authentication/login.html"),
         name='login_saft'),
    path("logout/", LogoutView.as_view(template_name='authentication/logged_out.html'),
         name="logout_saft"),
    path('i18n/', include("django.conf.urls.i18n")),

    path('debug/', include('debug_toolbar.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]

handler404 = "saft.utils.helpers.handle_not_found"  # vista del page not found 404

handler403 = "saft.utils.helpers.handle_permission_denied"  # vista del page not found 403

handler500 = "saft.utils.helpers.handle_server_error"  # vista del page not found 500
