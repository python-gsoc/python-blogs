from django.conf.urls import url, include

from . import views

urlpatterns = [
    url('^application/', include([
        url('^', views.register_suborg, name='register_suborg'),
        url('^thanks/', views.post_register, name='post_register'),
        url(r'^accept/(?P<application_id>[0-9]+)/', views.accept_application,
            name='accept_application'),
        url(r'^reject/(?P<application_id>[0-9]+)/', views.reject_application,
            name='reject_application'),
    ])),
    url('^mentor/', include([
        url('^add/', views.add_mentor, name='add_mentor')
    ])),
]
