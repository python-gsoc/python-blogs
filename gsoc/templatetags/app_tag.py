from django import template
import datetime
import django.utils.timezone as tz
import pytz
from dateutil.relativedelta import *
from django.shortcuts import render

register = template.Library()

"""
	This function makes use of the django timezone library to
	get the user's local time and pytz for getting utc time.
	Now, we use the common_timezones library in pytz to get 
	timezone of various places across the globe. 
	
	We calculate the difference between Utctime and localtime and compare
	the difference of utctime with those global timezones with 
	previously computed difference and accordingly, set the 
	timezone of the user.
"""
@register.simple_tag(takes_context=True)
def time_zone(context,flag=0):
    gmtTime = "+00:00"
    localTime = tz.now()
    utcTimeZone = pytz.timezone('UTC')
    utcTime = datetime.datetime.now(tz=utcTimeZone)
    all_timezones = pytz.common_timezones
    localDate = datetime.datetime.strftime(localTime.date(), '%d')
    utcDate = datetime.datetime.strftime(utcTime.date(), '%d')
    TIME_ZONE = "UTC"
    for i in all_timezones :
        timeZone = pytz.timezone(i)
        timeFromUTC = str(datetime.datetime.now(tz=timeZone))[-6:]
        time = datetime.datetime.now(tz=timeZone)
        if(time.hour == localTime.hour) :
            if(abs(time.minute-localTime.minute) <= 1 ) :
                TIME_ZONE = i
                gmtTime = timeFromUTC
                break
    if flag :
        return gmtTime
    else :
        return TIME_ZONE