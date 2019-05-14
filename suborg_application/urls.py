from django.conf.urls import url

from .views import register_suborg

urlpatterns = [
    url('^$', register_suborg, name='register_suborg'),
]
