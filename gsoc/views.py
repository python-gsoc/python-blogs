from django.shortcuts import render

def mail(request):
    return (request, 'task.html')

def output(request):
    #run python script
    return (request, 'task.html')