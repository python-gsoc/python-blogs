from django.conf.urls import url

from .views import list_blogs
from .feeds import BlogsFeed, ArticlesFeed

import aldryn_newsblog.urls

urlpatterns = [
    url("^$", list_blogs, name="list_blogs"),
    url("feed/$", BlogsFeed(), name="feed"),
    url(r"(?P<blog_slug>[\w-]+)/feed/", ArticlesFeed(), name="blog_feed"),
]
