import random

from django.shortcuts import render
from django.http import Http404

from gsoc.models import (
    GsocYear,
    UserProfile
)
from cms.models import Page

def list_blogs(request):
    gsoc_years = GsocYear.objects.all().order_by('-gsoc_year')
    
    blogsets = []
    for year in gsoc_years:
        profiles = UserProfile.objects.filter(gsoc_year=year)
        flag = False    

        blogset = []
        for profile in profiles:
            if profile.app_config:
                flag = True
                ns = profile.app_config.namespace
                page = Page.objects.filter(application_namespace=ns).filter(publisher_is_draft=False).first()
                url = page.get_absolute_url()
                student_name = profile.user.get_full_name()
                student_username = profile.user.username

                blogset.append({
                    'title': profile.app_config.app_title,
                    'url': url,
                    'student': student_name if student_name else student_username,
                    'suborg': profile.suborg_full_name.suborg_name,
                    'color': random.choice(['umber', 'khaki', 'wine', 'straw'])
                })
        
        if flag:
            blogsets.append((year.gsoc_year, blogset))

    return render(request, 'list_view.html', {
        'blogsets': blogsets
    })
