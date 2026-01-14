from django.urls import include, path

from . import auth as auth_urls
from . import call_center as call_center_urls

app_name = 'v1'

urlpatterns = [
    path('auth/', include(auth_urls.urlpatterns)),
    path('call-center/', include(call_center_urls.urlpatterns)),
]
