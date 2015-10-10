from datetime import timedelta, tzinfo

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils import timezone

from box.models import DriveBox, EventLog, Allowance

from pytz import utc


class BoxTestBase(TestCase):
    known_mac_address = '001122334455'
    unknown_mac_address = '001122334400'

    def setUp(self):
        self.box = DriveBox(mac=self.known_mac_address)
        self.box.save()


class ReportEventViewTests(BoxTestBase):
    def test_report_from_know_box(self, ev=0):
        url = '{0}?time={1}&event={2}'.format(reverse('box:report_event', args=(self.box.mac,)),
                                              '2015-03-21T01:29:00.50Z',
                                              str(ev))
        response = self.client.put(url)
        self.assertEqual(response.status_code, 201)

        events = EventLog.objects.filter(box=self.box, event=ev)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].time, timezone.datetime(2015, 3, 21, 1, 29, 0, 500000, tzinfo=utc))
        self.assertEqual(events[0].event, ev)

    def test_report_from_unknown_box(self):
        response = self.client.put('{0}?time={1}&event={2}'.format(reverse('box:report_event',
                                                                        args=(self.unknown_mac_address,)),
                                                                   '2015-03-21T01:29:00.50Z',
                                                                   '0'))
        self.assertEqual(response.status_code, 404)

    def arbitrary_time_string_test(self, time_string):
        response = self.client.put('{0}?time={1}&event={2}'.format(reverse('box:report_event', args=(self.box.mac,)),
                                                                   time_string,
                                                                   '0'))
        self.assertEqual(response.status_code, 400)

    def test_report_with_invalid_time_invalid_format(self):
        self.arbitrary_time_string_test('2015-03-21T01:200.50Z')

    def test_report_with_invalid_time_not_even_close(self):
        self.arbitrary_time_string_test('This is just wrong')

    def test_report_event_is_idempotent(self):
        for i in xrange(3):
            for j in xrange(3):
                self.test_report_from_know_box(j)
        events = EventLog.objects.filter()
        self.assertEqual(3, len(events))

    def test_event_is_printable(self):
        e = EventLog(box=self.box, time=timezone.datetime(2015, 3, 21, 1, 29, 0, 500000, tzinfo=utc), event=0)
        s = str(e)

    def test_only_accepts_puts(self):
        response = self.client.get('{0}?time={1}&event={2}'.format(reverse('box:report_event', args=(self.box.mac,)),
                                                                   '1',
                                                                   '0'))
        self.assertNotEqual(response.status_code, 200)


class GetAllowanceViewTests(BoxTestBase):
    interval = timedelta(hours=6)

    def setUp(self):
        BoxTestBase.setUp(self)

        start_time = timezone.now() - self.interval * 5
        self.test_time = timezone.now() + self.interval / 2
        time = timezone.now()

        while time < start_time + self.interval * 10:
            a = Allowance(box=self.box, start_time=time, end_time=time+self.interval, duration_sec=3600)
            a.save()
            time += self.interval

    def test_only_returns_future_allowance(self):
        response = self.client.get('{0}?time={1}'.format(reverse('box:get_allowance', args=(self.box.mac, 'bin')),
                                                         self.test_time.isoformat().replace('+00:00', 'Z')))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/octet-stream')
        from struct import calcsize, unpack_from

        allowance_entry = '<hbbbbbhbbbbbh'

        entry_size = calcsize(allowance_entry)

        entries = len(response.content) / entry_size

        self.assertEqual(entries, 5)

        for i in xrange(entries):
            unpacked = unpack_from(allowance_entry, response.content, entry_size * i)

            start_time = apply(timezone.datetime, unpacked[0:6] + (0, utc))
            end_time = apply(timezone.datetime, unpacked[6:12] + (0, utc))
            self.assertGreaterEqual(end_time, self.test_time)
            self.assertEqual(unpacked[12], 3600)
