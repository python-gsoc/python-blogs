from .models import (UserDetails, UserProfile, RegLink, BlogPostDueDate, Event,
                     SubOrgDetails)

from django import forms


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = (
            'role',
            'suborg_full_name',
            'gsoc_year',
            'accepted_proposal_pdf',
            'app_config',
            'hidden'
            )
        widgets = {
            'app_config': forms.Select(),
            }


class ProposalUploadForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['accepted_proposal_pdf']


class UserDetailsForm(forms.ModelForm):
    class Meta:
        model = UserDetails
        fields = ('deactivation_date',)


class RegLinkForm(forms.ModelForm):
    class Meta:
        model = RegLink
        fields = ('email', 'user_role', 'user_suborg', 'user_gsoc_year')


class BlogPostDueDateForm(forms.ModelForm):
    class Meta:
        model = BlogPostDueDate
        fields = ('title', 'date')


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('title', 'start_date', 'end_date')


class SubOrgApplicationForm(forms.ModelForm):
    class Meta:
        model = SubOrgDetails
        exclude = ('gsoc_year', )
