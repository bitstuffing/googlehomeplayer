from django.shortcuts import render

from utils.administrationUtils import AdministrationUtils

import pychromecast
from pychromecast import Chromecast, DeviceStatus, CAST_TYPES, CAST_TYPE_CHROMECAST
import json
import base64
import time

from utils.decoder import decodeUrl

from player.models import Device

MESSAGE_TYPE = 'type'
TYPE_PAUSE = "PAUSE"
REFRESH_TIME = 0.3

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
    Device.objects.all().delete()
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
    data = {}
    data["playing"] = str(finalUrl)
    if ("youtube." in finalUrl or "youtu." in finalUrl ) and "video" in request.POST and request.POST.get("video") == "true":
        audio = False
        from pychromecast.controllers.youtube import YouTubeController
        yt = YouTubeController()
        cast.register_handler(yt)
        finalUrl = finalUrl[finalUrl.rfind("=")+1:]
        yt.play_video(finalUrl)
    else:
        mc = cast.media_controller
        if "video" in request.POST and request.POST.get("video") is "false":
            audio = False
        try:
            playerUrl = decodeUrl(finalUrl,audio)
            data["decoded"] = playerUrl
        except Exception as ex:
            print(str(ex))
            playerUrl = finalUrl
            pass
        format = "video"
        if audio:
            format = "audio"
        mc.play_media(playerUrl,format)
    return AdministrationUtils.httpResponse(json.dumps(data))

def seek(request):
    storedCast = getStoredCast(request)
    storedCast.wait()
    mc = storedCast.media_controller
    time.sleep(REFRESH_TIME)
    data = {}
    data["seek"] = "false"
    if "seek" in request.POST:
        seekValue = request.POST.get("seek")
        mc.seek(seekValue)
        data["seek"] = str(seekValue)
    return AdministrationUtils.jsonResponse(data)

def stop(request):
    storedCast = getStoredCast(request)
    storedCast.wait()
    mc = storedCast.media_controller
    time.sleep(REFRESH_TIME)
    mc.stop()
    data = {}
    data["stop"] = "true"
    return AdministrationUtils.jsonResponse(data)

def pause(request):
    storedCast = getStoredCast(request)
    storedCast.wait()
    mc = storedCast.media_controller
    time.sleep(REFRESH_TIME)
    status = "true"
    if mc.status.player_state == "PLAYING":
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
    storedCast = getStoredCast(request)
    mc = storedCast.media_controller
    time.sleep(REFRESH_TIME)
    status = {}
    status["duration"] = mc.status.duration
    status["current"] = mc.status.current_time
    status["state"] = mc.status.player_state
    status["volume"] = storedCast.status.volume_level
    status["content"] = mc.status.content_id
    status["app"] = storedCast.status.display_name
    try:
        #storedCast.socket_client.socket.close()
        storedCast.socket_client.disconnect()
        storedCast.disconnect()
    except Exception as e:
        print(str(e))
        pass
    return AdministrationUtils.jsonResponse(status)

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
    try:
        integerId = int(request.POST.get("id"))
        device = Device.objects.get(id=integerId)
    except:
        device = Device.objects.latest('id')
        pass
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
