from django import template
import datetime
import django.utils.timezone as tz
import pytz
from dateutil.relativedelta import *
from django.shortcuts import render

register = template.Library()

@register.simple_tag(takes_context=True)
def time_zone(context,flag=0):
    global gmtTime
    localTime = tz.now()
    utcTimeZone = pytz.timezone('UTC')
    utcTime = datetime.datetime.now(tz=utcTimeZone)
    all_timezones = pytz.common_timezones
    localDate = datetime.datetime.strftime(localTime.date(),'%d')
    utcDate = datetime.datetime.strftime(utcTime.date(),'%d')
    isUtc = False
    isUtcAhead = True
    if utcDate < localDate:
        isUtcAhead = False
    elif utcDate == localDate :
        if localTime.hour > utcTime.hour:
            isUtcAhead = False
        elif localTime.hour == utcTime.hour:
            if localTime.minute > utcTime.minute:
                isUtcAhead = False
            elif localTime.minute == utcTime.minute:
                isUtc = True		
    TIME_ZONE = "UTC"
    if not isUtc:
        for i in all_timezones:
            timeZone = pytz.timezone(i)
            timeFromUTC = str(datetime.datetime.now(tz=timeZone))[-6:]
            time = datetime.datetime.now(tz=timeZone)
            if(time.hour == localTime.hour):
                if(abs(time.minute-localTime.minute) <= 1 ):
                    TIME_ZONE = i
                    break
    gmtTime = timeFromUTC
    if flag:
        return gmtTime
    else:
        return TIME_ZONE
	