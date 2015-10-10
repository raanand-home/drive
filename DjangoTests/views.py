from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render


def home(request):
    return HttpResponseRedirect(reverse('drive:index'))

from django import forms


class TestForm(forms.Form):
    name = forms.CharField(label="Name", max_length=30)


def test(request):
    if request.method == 'POST':
        form = TestForm(request.POST)
        if form.is_valid():
            return HttpResponse('OK')
    else:
        form = TestForm()

    return render(request, 'drive/base.html', {'form': form})
