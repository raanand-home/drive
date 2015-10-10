from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',
    url(r'^$', 'DjangoTests.views.home', name='home'),
    url(r'test.html', 'DjangoTests.views.test', name='test'),
    url(r'^drive/', include('drive.urls', namespace='drive')),
    url(r'^box/', include('box.urls', namespace='box')),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()