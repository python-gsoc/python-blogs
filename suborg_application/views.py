from gsoc.forms import SubOrgApplicationForm

from django.shortcuts import render


def register_suborg(request):
    if request.method == 'GET':
        form = SubOrgApplicationForm()
        return render(request, 'register_suborg.html', {
            'form': form,
        })