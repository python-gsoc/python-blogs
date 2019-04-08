#import time

from django.contrib.auth.models import User
from .irc import send_message


def send_email(scheduler):
    # time.sleep(10)
    return 'Test Error'


def deactivate_user(scheduler):
    """
    makes a user inactive when scheduled
    """
    u = User.objects.filter(pk=scheduler.data).first()
    u.is_active = False
    u.save()
    scheduler.success = True
    scheduler.save()
    return None


def send_irc_msgs(schedulers):
    """
    sends the irc messages from `send_irc_msg` `Scheduler` objects
    and returns any error encountered
    """
    send_message([_.data for _ in schedulers])
    for s in schedulers:
        s.success = True
        s.save()
    return None
