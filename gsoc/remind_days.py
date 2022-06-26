from .models import DaysConf


# days
PRE_BLOG_REMINDER = DaysConf.objects.get(title="PRE_BLOG_REMINDER")
POST_BLOG_REMINDER_FIRST = DaysConf.objects.get(title="POST_BLOG_REMINDER_FIRST")
POST_BLOG_REMINDER_SECOND = DaysConf.objects.get(title="POST_BLOG_REMINDER_SECOND")

BLOG_POST_DUE_REMINDER = DaysConf.objects.get(title="BLOG_POST_DUE_REMINDER")
UPDATE_BLOG_COUNTER = DaysConf.objects.get(title="UPDATE_BLOG_COUNTER")

REGLINK_REMINDER = DaysConf.objects.get(title="REGLINK_REMINDER")
