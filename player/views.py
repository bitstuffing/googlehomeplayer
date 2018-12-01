from django.shortcuts import render

from utils.administrationUtils import AdministrationUtils

import pychromecast
from pychromecast import Chromecast, DeviceStatus, CAST_TYPES, CAST_TYPE_CHROMECAST
import json
import base64

from utils.decoder import decodeUrl

from player.models import Device

MESSAGE_TYPE = 'type'
TYPE_PAUSE = "PAUSE"

def index(request):
    context = { }
    if Device.objects.count():
        device = Device.objects.latest("id")
        id = device.id
        name = device.friendly_name
        context["id"] = id
        context["name"] = name
    return AdministrationUtils.render(request,'player/index.html',context)

def select_device(request,target):
    chromecasts = pychromecast.get_chromecasts()
    cast = next(cc for cc in chromecasts if cc.device.friendly_name == target)
    #request.session["ip_address"] = cast.host
    #request.session["port"] = cast.port
    #request.session["friendly_name"] = target
    #request.session["model_name"] = cast.model_name
    #request.session["uuid"] = str(cast.uuid)
    device = Device()
    device.ip_address = cast.host
    device.port = cast.port
    device.friendly_name = target
    device.model_name = cast.model_name
    device.uuid = str(cast.uuid)
    device.save()
    data = {}
    data["target"] = target
    data["id"] = device.id
    return AdministrationUtils.jsonResponse(data)

def get_devices(request):
    chromecasts = pychromecast.get_chromecasts()
    devices = []
    for cc in chromecasts:
        devices.append(cc.device.friendly_name)
    elements = json.dumps(devices)
    return AdministrationUtils.httpResponse(elements)

def play(request):
    url = request.POST.get("url")
    audio = True
    cast = getStoredCast(request)
    finalUrl = base64.b64decode(url).decode("utf-8")
    if "youtube." in finalUrl and "video" in request.POST and request.POST.get("video"):
        audio = False
        from pychromecast.controllers.youtube import YouTubeController
        yt = YouTubeController()
        cast.register_handler(yt)
        finalUrl = finalUrl[finalUrl.rfind("=")+1:]
        yt.play_video(finalUrl)
    else:
        mc = cast.media_controller
        if "video" in request.POST and request.POST.get("video"):
            audio = False
        try:
            playerUrl = decodeUrl(finalUrl,audio)
        except Exception as ex:
            print(str(ex))
            playerUrl = finalUrl
            pass
        format = "video"
        if audio:
            format = "audio"
        mc.play_media(playerUrl,format)
    data = {}
    data["playing"] = str(finalUrl)
    return AdministrationUtils.httpResponse(json.dumps(data))

def stop(request):
    cast = getStoredCast(request)
    mc = cast.media_controller
    mc.block_until_active()
    mc.stop()
    data = {}
    data["stop"] = "true"
    return AdministrationUtils.jsonResponse(data)

def pause(request):
    cast = getStoredCast(request)
    mc = cast.media_controller
    mc.block_until_active(timeout=2)
    status = "true"
    if mc.player_state == MEDIA_PLAYER_STATE_PLAYING:
        mc.pause()
    else:
        status = "false"
        mc.play()
    data = {}
    data["pause"] = status
    return AdministrationUtils.jsonResponse(data)

def volume(request):
    cast = getStoredCast(request)
    cast.wait()
    status = cast.status
    vol = status.volume_level
    up = False
    if "up" in request.POST and request.POST.get("up") == "true":
        vol = vol+0.1
    else:
        vol = vol-0.1
    #status.volume_level = vol
    cast.set_volume(vol)
    cast.wait()
    return AdministrationUtils.httpResponse(str(cast))

def track(request):
    cast = getStoredCast(request)
    cast.wait()
    mc = cast.media_controller
    mc.block_until_active()
    if "back" in request.POST and request.POST.get("back") == "true":
        pass
    elif "forward" in request.POST and request.POST.get("forward") == "true":
        pass
    return AdministrationUtils.httpResponse(str(str(mc.status)))

def getCast(request):
    friendly_name = request.session["friendly_name"]
    model_name = request.session["model_name"]
    uuid = request.session["uuid"]
    ip_address = request.session["ip_address"]
    port = request.session["port"]
    cast_type = CAST_TYPES.get(model_name.lower(), CAST_TYPE_CHROMECAST)
    device = DeviceStatus(
        friendly_name=friendly_name, model_name=model_name,
        manufacturer=None, uuid=uuid, cast_type=cast_type
    )
    cast = Chromecast(host=ip_address, port=port, device=device)
    return cast

def getStoredCast(request):
    device = Device.objects.get(id=int(request.POST.get("id")))
    friendly_name = device.friendly_name
    model_name = device.model_name
    uuid = device.uuid
    ip_address = device.ip_address
    port = device.port
    cast_type = CAST_TYPES.get(model_name.lower(), CAST_TYPE_CHROMECAST)
    device = DeviceStatus(
        friendly_name=friendly_name, model_name=model_name,
        manufacturer=None, uuid=uuid, cast_type=cast_type
    )
    cast = Chromecast(host=ip_address, port=int(port), device=device)
    return cast
