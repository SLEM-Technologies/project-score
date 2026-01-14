from django.urls import path, include

from api.urls import urlpatterns as api_urlpatterns
from apps.admin.admin import vetsuccess_admin_site

urlpatterns = [
    path('api/', include(api_urlpatterns)),
    path('admin/', vetsuccess_admin_site.urls),
]
