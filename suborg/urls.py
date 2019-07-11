from django.conf.urls import url, include

from . import views

urlpatterns = [
    url('^$', views.home, name='home'),
    url('^application/', include([
        url('^$', views.application_list, name='application_list'),
        url('^new/', views.register_suborg, name='register_suborg'),
        url('^update/(?P<application_id>[0-9]+)/', views.update_application,
            name='update_application'),
        url('^thanks/', views.post_register, name='post_register'),
        url(r'^accept/(?P<application_id>[0-9]+)/', views.accept_application,
            name='accept_application'),
        # url(r'^reject/(?P<application_id>[0-9]+)/', views.reject_application,
        #     name='reject_application'),
    ])),
    url('^mentor/', include([
        url('^add/(?P<application_id>[0-9]+)/', views.add_mentor, name='add_mentor')
    ])),
]
