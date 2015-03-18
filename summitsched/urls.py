from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'cheddar.views.index'),
    url(r'^openid/', include('django_openid_auth.urls')),
    url(r'^cheddar/', include('cheddar.urls', namespace="cheddar")),
    url(r'^admin/', include(admin.site.urls)),
)
