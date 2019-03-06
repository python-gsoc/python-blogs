from django.forms import ModelForm, CheckboxSelectMultiple

from .models import UserProfile,SubOrgForm


class UserProfileForm(ModelForm):
    class Meta:
        fields = ('suborg_full_name', 'gsoc_year')
        model = UserProfile
        widgets = {
            'suborg_full_name': CheckboxSelectMultiple(),
            'gsoc_year': CheckboxSelectMultiple()
        }

class SubOrgForm(ModelForm):
    class Meta:
        model = SubOrgForm
        fields = ('user', 'Idea List','blog')
