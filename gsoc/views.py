from django.http import HttpResponse
from aldryn_newsblog.models import Article
from django.shortcuts import render

def blog(request):
    articles=Article.objects.all()
    data = {}
    for article in articles:
        data[article.title] = article.get_search_data()
    context = {"data" : data}
    return render(request, 'student-blogs.html', context)
	
def article(request, article_id):
    articles=Article.objects.all()
    data={}
    for article in articles:
        if article.slug == article_id:
            data[article.title] = article.get_search_data()
            break
    context = {"data" : data}
    return render(request, 'student-blogs.html', context)
