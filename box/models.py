from django.db import models


class DriveBox(models.Model):
    """"""
    """The MAC address of the DriveBox"""
    mac = models.CharField(max_length=17, db_index=True)
    control = models.BooleanField(default=False)

    @property
    def status(self):
        ev = EventLog.objects.filter(box=self).order_by('-time')
        if (len(ev) > 0):
            return ev[0].event == 1
        else:
            return False

    def __unicode__(self):
        return self.mac


class EventLog(models.Model):
    box = models.ForeignKey(DriveBox, db_index=True)
    time = models.DateTimeField(db_index=True)
    event = models.IntegerField()

    def __unicode__(self):
        return '{0}, {1}, {2}'.format(self.box, self.time, self.event)


class Allowance(models.Model):
    box = models.ForeignKey(DriveBox, db_index=True)
    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField(db_index=True)
    duration_sec = models.IntegerField()

    def __unicode__(self):
        return '{0} -> {1}: {2}'.format(self.start_time, self.end_time, self.duration_sec)