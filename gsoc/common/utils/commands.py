import time

from .irc import send_message

def send_email(scheduler):
    # time.sleep(10)
    return 'Test Error'

def send_irc_msgs(schedulers):
    """
    sends the irc messages from `send_irc_msg` `Scheduler` objects
    and returns any error encountered
    """
    send_message([_.data for _ in schedulers])
    for s in schedulers:
        s.success=True
        s.save()
    return None
