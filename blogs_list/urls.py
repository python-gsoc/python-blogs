from django.conf.urls import url

from .views import list_blogs

urlpatterns = [
    url('^$', list_blogs, name='list_blogs'),
]
