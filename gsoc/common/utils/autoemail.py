from datetime import *

from django.db import models
from gsoc.models import UserProfile
from django.contrib.auth.models import User
from django.core.mail import send_mail
from gsoc.models import UserProfile
from aldryn_newsblog.models import Article

#Really horrible code ahead. Be careful.

def SentMail():
    email_list_count=len(UserProfile.objects.all())
    
    for i in range(1,email_list_count+1):
        user = User.objects.get(id=i)
        user_name= user.get_username()
        user_role=UserProfile.objects.role 
        article=list(Article.objects.filter(author=user_name))
        article=article[::-1]
        duration=article[0].publishing_date - datetime.now()
        if (user_role == 3) and (duration.days >= 7):
            send_mail(
            'It\'s been 7 days',
            'Post something already.',
            'from@example.com',
            [user.email],
            fail_silently=False,
        )