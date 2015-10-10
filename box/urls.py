from django.conf.urls import patterns, url

from box import views


hex_digit = r'[0-9a-fA-F]'
mac_address = hex_digit * 2 * 6

urlpatterns = patterns('',
                       url(r'(?P<mac>' + mac_address + r')/' +
                           r'report_event',
                           views.report_event, name='report_event'),
                       url(r'(?P<mac>' + mac_address + r')/' +
                           r'get/' +
                           r'allowances.(?P<fmt>[^/]+)',
                           views.get_allowance, name='get_allowance'),
                       )
