from django.urls import path
from django.urls import include, re_path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('devices/', views.get_devices, name='get_devices'),
    re_path('^device/(.*)/$', views.select_device, name='select_device'),
    re_path('^play/', views.play, name='play'),
    re_path('^stop/', views.stop, name='stop'),
    re_path('^pause/', views.pause, name='pause'),
    re_path('^volume/', views.volume, name='volume'),
    re_path('^seek/', views.seek, name='seek'),
    re_path('^track/', views.track, name='track'),
    re_path('^playlist/', views.playlist, name='playlist'),
    re_path('^control/', views.control, name='playlist'),
]
