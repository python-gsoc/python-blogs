from django.db import models
from gsoc.models import UserProfile
from django.core.mail import send_mail

#Really horrible code ahead. Be careful.
#Need to add whether the post is 7 days old or not.
email_list_count=len(UserProfile.objects.all())

for i in range(1,email_list_count+1):
    temp_dict=UserProfile.objects.get(id=1).values('email_id')
    send_mail(
    'It\'s been 7 days',
    'Post something already.',
    'from@example.com',
    [temp_dict['email_id']],
    fail_silently=False,
    )