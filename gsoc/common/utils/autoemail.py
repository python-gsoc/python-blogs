from django.db import models
from gsoc.models import UserProfile
from django.contrib.auth.models import User
from django.core.mail import send_mail
from aldryn_newsblog.models import Article

#Really horrible code ahead. Be careful.
#Need to add whether the post is 7 days old or not.

def SentMail():
    email_list_count=len(UserProfile.objects.all())
    
    for i in range(1,email_list_count+1):
        user = User.objects.get(id=i)
        user_email = user.email
        user_name= user.get_username()
        article=Article.objects.filter(author=user_name)
        if article.publishing_date > 7:
            send_mail(
            'It\'s been 7 days',
            'Post something already.',
            'from@example.com',
            [user_email],
            fail_silently=False,
        )