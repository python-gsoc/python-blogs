from django.urls import path
from .views import index, form, handle_submit
urlpatterns = [
    path('', index),
    path('form/', form, name='suborg-submit-form'),
]
