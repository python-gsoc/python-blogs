from .models import UserDetails, UserProfile

from django.forms import ModelForm, Select


class UserProfileForm(ModelForm):
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
            'app_config': Select(),
            }


class ProposalUploadForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['accepted_proposal_pdf']


class UserDetailsForm(ModelForm):
    class Meta:
        model = UserDetails
        fields = ('deactivation_date',)
