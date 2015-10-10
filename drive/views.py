from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User as authUser
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from models import ScreenLockUser, Household, HouseholdBoxes
from box.models import DriveBox

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST


@login_required
def index(request):
    screen_lock_user = ScreenLockUser.objects.get(user=request.user)
    context = RequestContext(request)
    return render_to_response('drive/index.html',
                              {
                                  'screen_lock_user': screen_lock_user,
                                  'home': True
                              },
                              context)


@login_required
def household(request):
    context = RequestContext(request)
    screen_lock_user = get_object_or_404(ScreenLockUser, user=request.user)
    additional_context = {'screen_lock_user': screen_lock_user}

    if screen_lock_user.has_household():
        additional_context.update({'caretakers': screen_lock_user.household.screenlockuser_set.filter(caretaker=True),
                                   'children': screen_lock_user.household.screenlockuser_set.filter(caretaker=False),
                                   'boxes': screen_lock_user.household.householdboxes_set.filter(),
                                   'household': True,
                                   })

        if screen_lock_user.caretaker:
            additional_context.update(
                {'join_requests': screen_lock_user.household.join_request_set.filter()})

        return render_to_response('drive/household.html',
                                  additional_context,
                                  context)
    elif screen_lock_user.has_join_request():
        additional_context.update(
            {'join_request_household': screen_lock_user._join_request})

        return render_to_response('drive/active_join_request.html',
                                  additional_context,
                                  context)
    else:
        return render_to_response('drive/no_household.html',
                                  additional_context,
                                  context)


@login_required
@require_POST
def join_request(request):
    context = RequestContext(request)
    screen_lock_user = get_object_or_404(ScreenLockUser, user=request.user)
    action = request.POST['action']
    household_name = request.POST['household']

    if action == 'create':
        if len(Household.objects.filter(name=household_name)) == 0:
            household = Household(name=household_name)
            household.save()
            screen_lock_user.household = household
            screen_lock_user.caretaker = True
        else:
            return HttpResponse('Household already exists')
    elif action == 'join':
        screen_lock_user._join_request = get_object_or_404(Household, name=household_name)

    screen_lock_user.save()

    return HttpResponseRedirect(reverse('drive:household'))


@login_required
@require_POST
def join_reply(request):
    screen_lock_user = ScreenLockUser.objects.get(user=request.user)
    household = screen_lock_user.household

    requesting_user = household.join_request_set.get(pk=request.POST['requesting_user_pk'])
    if request.POST['action'] == u'accept':
        requesting_user.household = household
        requesting_user._join_request = None
        requesting_user.caretaker = False
    elif request.POST['action'] == u'reject':
        requesting_user._join_request = None
    requesting_user.save()

    return HttpResponseRedirect(reverse('drive:household'))


def box_join(request):
    box = get_object_or_404(DriveBox, mac=request.GET['mac'])
    if len(HouseholdBoxes.objects.filter(box=box)) > 0:
        return HttpResponse(status=409)

    user = get_object_or_404(ScreenLockUser, user__email=request.GET['user_email'])
    hb = HouseholdBoxes(household=user.household, box=box, alias=box.mac)
    hb.save()
    return HttpResponse()


@login_required
@require_POST
def box_control(request):
    screen_lock_user = ScreenLockUser.objects.get(user=request.user)
    box = screen_lock_user.household.householdboxes_set.get(box__mac=request.POST['box']).box

    action = request.POST['action']

    box.control = action == 'enable'
    box.save()
    return HttpResponseRedirect(reverse('drive:household'))


def register(request):
    context = RequestContext(request)

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        password_ver = request.POST['password_ver']
        nickname = request.POST['nickname']
        email = request.POST['email']

        if password != password_ver:
            return HttpResponse("Password mismatch!")

        try:
            authUser.objects.get(username=username)
            return HttpResponse("Can't register user, try a different username.")
        except authUser.DoesNotExist:
            pass  # Good, we can create your username.

        new_auth_user = authUser(username=username, email=email)
        new_auth_user.set_password(raw_password=password)
        new_auth_user.save()

        user = ScreenLockUser(user=new_auth_user, nickname=nickname)
        user.save()

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return HttpResponseRedirect(reverse('drive:index'))
        else:
            return HttpResponse("Can't register user, unknown error.")

    # The request is not a HTTP POST, so display the registration form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render_to_response('drive/register.html', {'register': True}, context)


def user_login(request):
    context = RequestContext(request)

    next = ''

    if request.GET:
        next = request.GET['next']

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                if next == '':
                    return HttpResponseRedirect(reverse('drive:index'))
                else:
                    return HttpResponseRedirect(next)
            else:
                return HttpResponse("Your Drive account is disabled.")
        else:
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render_to_response('drive/login.html',
                                  {
                                      'next': next,
                                      'login': True
                                  },
                                  context)


def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('drive:index'))
