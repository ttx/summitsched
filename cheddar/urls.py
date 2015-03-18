from django.conf.urls import patterns, url

from cheddar import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(\d+)$', views.trackindex),
    url(r'^logout$', views.dologout),
    url(r'^loggedout$', views.loggedout),
)
