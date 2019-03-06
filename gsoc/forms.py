from django.forms import ModelForm, CheckboxSelectMultiple

from .models import UserProfile


class UserProfileForm(ModelForm):
    class Meta:
        fields = ('role', 'suborg_full_name', 'gsoc_year')
        model = UserProfile
