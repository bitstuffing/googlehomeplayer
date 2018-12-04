from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('devices/', views.get_devices, name='get_devices'),
    url('^device/(\w+)/$', views.select_device, name='select_device'),
    url('^play/', views.play, name='play'),
    url('^stop/', views.stop, name='stop'),
    url('^pause/', views.pause, name='pause'),
    url('^volume/', views.volume, name='volume'),
    url('^seek/', views.seek, name='seek'),
    url('^track/', views.track, name='track'),
]
