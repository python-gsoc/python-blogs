from django.contrib import auth
from django.db import models
from django.contrib.auth.models import User


class Scheduler(models.Model):
    commands = (
        ('send_email', 'send_email'),
        ('send_irc_msg', 'send_irc_msg')
    )
    
    id = models.AutoField(primary_key=True)
    command = models.CharField(name='command', max_length=20, choices=commands)
    data = models.TextField(name='data')
    success = models.BooleanField(name='success', null=True)
    last_error = models.TextField(name='last_error', null=True, default=None)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.command
class SubOrgForm(models.Model):

    id = models.AutoField(primary_key=True)
    user = models.CharField(name='user',max_length=40)
    reason = models.CharField(name='Why does your org want to participate in Google Summer of Code?', max_length=200)
    num_of_mentor = models.IntegerField(name='How many potential mentors have agreed to mentor this year?')
    suborg_admin_email = models.EmailField(name='suborg_admin_email',)
    mentor_email = models.EmailField(name='mentor_email',)
    schedule = models.CharField(name='How will you help your students stay on schedule to complete their projects?', max_length=200)
    get_involve = models.CharField(name='How will you get your students involved in your community during GSoC?', max_length=200)
    keep_involve = models.CharField(name='How will you keep students involved with your community after GSoC?', max_length=200)
    accepted = models.BooleanField(name='Has your org been accepted as a mentor org in Google Summer of Code before?',default='no')
    accepted_years = models.CharField(name='Which years did your org participate in GSoC?',max_length=70)
    is_suborg = models.BooleanField(name='Was this as a Suborg?')
    participated_years = models.CharField(name='For each year your organization has participated, provide the counts of successful and total students. (e.g. 2016: 3/4)', max_length=10)
    not_selected_years = models.IntegerField(name='If your org has applied for GSoC before but not been accepted, write the years. e.g 2005,2017,2018')
    project_started = models.IntegerField(name='What year was your project started?')
    source_code = models.URLField(name='Where does your source code live?',default='https://github.com/XYZ')
    url = models.URLField(name='Please provide URLs that point to repositories, GitHub organizations, or a web page that describes how to get your source code.',default='xyz')
    anything = models.CharField(name='Anything Else ?',max_length=250)
    #public profile
    name = models.CharField(name='Name', max_length=30)
    website_url = models.URLField(name='Website URL',default='xyz')
    #desc
    #image=models.ImageField(upload_to='profile_image', blank=True)
    desc = models.CharField(name='A very short description of your organization.', max_length=250)
    #License
    licence = models.CharField(name='License Name', max_length=10, default='MIT')
    #Idea List
    idea_list = models.URLField(name='Idea List')
    #Chat
    irc_help = models.URLField(name='irc_help')
    #Mailing List
    mailing_list = models.URLField(name='mailing_list')
    #Links
    twitter = models.URLField(name='twitter')
    blog = models.URLField(name='blog')

    def __str__(self):
        return self.user

class SubOrg(models.Model):# SubOrg name
    suborg_name = models.CharField(name='suborg_name', max_length=80)

    def __str__(self):
        return self.suborg_name


class GsocYear(models.Model):# Gsoc Year
    gsoc_year = models.IntegerField(name='gsoc_year')

    def __str__(self):
        return str(self.gsoc_year)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gsoc_year = models.ManyToManyField(GsocYear, blank=True)
     

def suborg_full_name(self):
    try:
        user_profile = UserProfile.objects.get(user=self.id)
        return user_profile.suborg_full_name.all()
    except SubOrg.DoesNotExist:
        return None


def gsoc_year(self):
    try:
        user_profile = UserProfile.objects.get(user=self.id)
        return user_profile.gsoc_year.all()
    except GsocYear.DoesNotExist:
        return None
        
            
auth.models.User.add_to_class('suborg_full_name', suborg_full_name)
auth.models.User.add_to_class('gsoc_year', gsoc_year)
