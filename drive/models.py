from django.db import models
from django.contrib.auth.models import User as AuthUser
from box.models import DriveBox


class Household(models.Model):
    name = models.CharField(max_length=32, unique=True)
    boxes = models.ManyToManyField(DriveBox, through='HouseholdBoxes', blank=True)

    def __unicode__(self):
        return self.name


class ScreenLockUser(models.Model):
    user = models.OneToOneField(AuthUser)
    household = models.ForeignKey(Household, null=True, db_index=True, blank=True)
    nickname = models.CharField(max_length=32)
    caretaker = models.BooleanField(default=False)
    credits = models.IntegerField(default=0)

    _join_request = models.ForeignKey(Household, null=True, blank=True, related_name='join_request_set')

    def __unicode__(self):
        return u'{0}{1}'.format(self.nickname, u'+' if self.caretaker else u'')

    def has_household(self):
        return self.household is not None

    def has_join_request(self):
        return self._join_request is not None


class HouseholdBoxes(models.Model):
    household = models.ForeignKey(Household)
    box = models.ForeignKey(DriveBox, unique=True)
    alias = models.CharField(max_length=32)

    class Meta:
        unique_together = (('household', 'alias'),)

    def __unicode__(self):
        return self.alias


class ChoreStates:
    def __init__(self):
        pass

    incomplete = 0
    pending_approval = 1
    done = 2


class Chores(models.Model):
    user = models.ForeignKey(ScreenLockUser)
    name = models.CharField(max_length=32)
    state = models.IntegerField(default=ChoreStates.incomplete)
    date = models.DateField()
    credits = models.IntegerField(default=1)

    def __unicode__(self):
        return self.name


class Rewards(models.Model):
    name = models.CharField(max_length=32)
    household = models.ForeignKey(Household)
    credits = models.IntegerField(default=1)

    def __unicode__(self):
        return self.name