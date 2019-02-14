from django.http import HttpResponse
from gsoc.common.utils.irc import send_message

def irc_test(request):
    send_message("message")
    return HttpResponse("<body>test</body>")