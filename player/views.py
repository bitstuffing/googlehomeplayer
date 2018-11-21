from django.shortcuts import render

from utils.administrationUtils import AdministrationUtils

import pychromecast
import json

def index(request):
    context = {}
    return AdministrationUtils.render(request,'player/index.html',context)

def select_device(request,target):
    request.session["device"] = target
    data = {}
    data["target"] = target
    return AdministrationUtils.jsonResponse(data)

def get_devices(request):
    chromecasts = pychromecast.get_chromecasts()
    devices = []
    for cc in chromecasts:
        devices.append(cc.device.friendly_name)
    elements = json.dumps(devices)
    return AdministrationUtils.httpResponse(elements)

def play(request,url):
    chromecasts = pychromecast.get_chromecasts()
    target = request.session["device"]
    cast = next(cc for cc in chromecasts if cc.device.friendly_name == target)
    mc = cast.media_controller
    finalUrl = base64.decodestring(url)
    mc.play_media(finalUrl,"audio/mp3")
    data = {}
    data["url"] = url
    return AdministrationUtils.jsonResponse(data)
