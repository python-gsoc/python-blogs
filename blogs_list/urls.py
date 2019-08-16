from django.conf.urls import url

from .views import list_blogs
from .feeds import BlogsFeed

urlpatterns = [
    url("^$", list_blogs, name="list_blogs"),
    url("feed/", BlogsFeed(), name="feed"),
]
