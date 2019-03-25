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
        user_profile_object=UserProfile.objects.all()
        user_profile=user_profile_object[i-1]
        article=Article.objects.filter(owner=user)
        duration=datetime.now() - article[0].publishing_date
        print(user.email)
        if (user_profile.role == 3) and (duration.days >= 7):
            send_mail(
            'It\'s been 7 days',
            'Post something already.',
            'from@example.com',
            [user.email],
            fail_silently=False,
        )