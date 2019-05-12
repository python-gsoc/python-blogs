from .models import UserDetails, UserProfile, RegLink, Event

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


class EventForm(forms.ModelForm):
    add_calendar_event = forms.BooleanField(label='Add to calendar?')
    starts_from = forms.DateField(label='Starts from before',
                                  help_text='Enter the number of days before the\
                                             event you want the users to be notified')
    frequency = forms.IntegerField(help_text='Enter the frequency of notifications (in days)',
                                   min_value=1, max_value=4)

    class Meta:
        model = Event
        fields = '__all__'
