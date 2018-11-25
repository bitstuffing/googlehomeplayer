from django.shortcuts import render

from utils.administrationUtils import AdministrationUtils

import pychromecast
from pychromecast import Chromecast, DeviceStatus, CAST_TYPES, CAST_TYPE_CHROMECAST
import json
import base64

from utils.decoder import decodeUrl

MESSAGE_TYPE = 'type'
TYPE_PAUSE = "PAUSE"

def index(request):
    context = {}
    return AdministrationUtils.render(request,'player/index.html',context)

def select_device(request,target):
    chromecasts = pychromecast.get_chromecasts()
    cast = next(cc for cc in chromecasts if cc.device.friendly_name == target)
    request.session["ip_address"] = cast.host
    request.session["port"] = cast.port
    request.session["friendly_name"] = target
    request.session["model_name"] = cast.model_name
    request.session["uuid"] = str(cast.uuid)
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

def play(request):
    url = request.POST.get("url")
    cast = getCast(request)
    mc = cast.media_controller
    finalUrl = base64.b64decode(url).decode("utf-8")
    try:
        playerUrl = decodeUrl(finalUrl)
    except Exception as ex:
        print(str(ex))
        playerUrl = finalUrl
        pass
    print(playerUrl)
    mc.play_media(playerUrl,"audio/mp3")
    data = {}
    data["playing"] = str(finalUrl)
    return AdministrationUtils.httpResponse(json.dumps(data))

def stop(request):
    cast = getCast(request)
    mc = cast.media_controller
    mc.block_until_active()
    mc.stop()
    data = {}
    data["stop"] = "true"
    return AdministrationUtils.jsonResponse(data)

def pause(request):
    cast = getCast(request)
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
    cast = getCast(request)
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
    cast = getCast(request)
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
