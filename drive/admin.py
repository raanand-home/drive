from django.contrib import admin
from .models import Household, ScreenLockUser, Chores, Rewards, HouseholdBoxes


class BoxesInline(admin.TabularInline):
    model = HouseholdBoxes
    extra = 0


class UsersInline(admin.TabularInline):
    model = ScreenLockUser
    fk_name = 'household'
    extra = 0


class HouseholdJoinRequestInLine(admin.TabularInline):
    model = ScreenLockUser
    fk_name = '_join_request'
    extra = 0

@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    inlines = [
        UsersInline,
        BoxesInline,
        HouseholdJoinRequestInLine,
    ]


admin.site.register(ScreenLockUser)
