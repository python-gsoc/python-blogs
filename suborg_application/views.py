from gsoc.forms import SubOrgApplicationForm
from gsoc.models import GsocYear

from django.shortcuts import render, redirect
from django.urls import reverse


def register_suborg(request):
    if request.method == 'GET':
        gsoc_year = GsocYear.objects.first()
        form = SubOrgApplicationForm(initial={'gsoc_year': gsoc_year})
    
    elif request.method == 'POST':
        form = SubOrgApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            suborg_details = form.save()
            return redirect(reverse('suborg_application:post_register'))

    return render(request, 'register_suborg.html', {
            'form': form,
        })


def post_register(request):
    if request.method == 'GET':
        return render(request, 'post_register.html')
