from django.conf.urls import url

from .views import register_suborg, post_register

urlpatterns = [
    url('^$', register_suborg, name='register_suborg'),
    url('^thanks/', post_register, name='post_register'),
]
