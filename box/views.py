from struct import pack
import json

from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods, require_GET

from dateutil import parser as iso8601_parser

from box.models import DriveBox, EventLog, Allowance

from pytz import utc


@require_http_methods(['PUT'])
def report_event(request, mac):
    box = get_object_or_404(DriveBox, mac=mac)

    try:
        time = request.GET['time']
        event = request.GET['event']
        time = iso8601_parser.parse(time, tzinfos=[utc])
        event = int(event)
    except KeyError as ke:
        return HttpResponse(ke.message, status=400)
    except ValueError as ve:
        return HttpResponse(ve.message, status=400)

    event_exists = len(EventLog.objects.filter(box=box, time=time, event=event)) > 0

    if not event_exists:
        new_event = EventLog(box=box, time=time, event=event)
        new_event.save()

    return HttpResponse(status=201)


def pack_datetime(d):
    return pack('<hbbbbb', d.year, d.month, d.day, d.hour, d.minute, d.second)


time_elements = ('year', 'month', 'day', 'hour', 'minute', 'second')


def get_time_elements(d):
    return {el: getattr(d, el) for el in time_elements}


@require_http_methods(['GET'])
def get_allowance(request, mac, fmt):
    if 'time' not in request.GET:
        return HttpResponse(status=400)

    time = request.GET['time']

    box = get_object_or_404(DriveBox, mac=mac)
    future_allowances = Allowance.objects.filter(box=box, end_time__gte=iso8601_parser.parse(time))
    if fmt == 'bin':
        result = ''
        for allowance in future_allowances:
            result += pack_datetime(allowance.start_time) + pack_datetime(allowance.end_time) + \
                pack('<h', allowance.duration_sec)
        return HttpResponse(result, content_type='application/octet-stream')
    elif fmt == 'json':
        return JsonResponse(json.dumps({'Allowances': [{'start_date': get_time_elements(allowance.start_time),
                                                        'end_date': get_time_elements(allowance.end_time),
                                                        'duration_sec': allowance.duration_sec}
                                                       for allowance in future_allowances]}))
    else:
        return HttpResponse(status=415)
