from django.conf.urls import url

from .views import register_suborg, post_register, accept_application, reject_application

urlpatterns = [
    url('^$', register_suborg, name='register_suborg'),
    url('^thanks/', post_register, name='post_register'),
]

# Review application routes
urlpatterns += [
    url(r'^accept/(?P<application_id>[0-9]+)/$', accept_application,
        name='accept_application'),
    url(r'^reject/(?P<application_id>[0-9]+)/$', reject_application,
        name='reject_application'),
]
