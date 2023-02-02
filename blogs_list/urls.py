from django.conf.urls import url

from .views import list_blogs
from .feeds import BlogsFeed, ArticlesFeed



urlpatterns = [
    url("^$", list_blogs, name="list_blogs"),
    url("feed/$", BlogsFeed(), name="feed"),
    url(r"feed/(?P<blog_slug>[\w-]+)/", ArticlesFeed(), name="blog_feed"),
]
