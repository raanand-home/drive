from django.contrib import admin

from .models import DriveBox, EventLog, Allowance


class EventsInline(admin.StackedInline):
    model = EventLog
    extra = 0


class AllowanceInline(admin.StackedInline):
    model = Allowance
    extra = 0


class BoxAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['mac']})
    ]
    inlines = [EventsInline, AllowanceInline]


admin.site.register(DriveBox, BoxAdmin)
