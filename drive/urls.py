from django.conf.urls import patterns, url

from drive import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^login/$', views.user_login, name='login'),
                       url(r'^register/$', views.register, name='register'),
                       url(r'^logout/$', views.user_logout, name='logout'),
                       url(r'^household/$', views.household, name='household'),
                       url(r'^household/join_reply/$', views.join_reply, name='join_reply'),
                       url(r'^household/join_request/$', views.join_request, name='join_request'),
                       url(r'^household/box_join/$', views.box_join, name='box_join'),
                       url(r'^household/box_control/$', views.box_control, name='box_control'),
                       )
