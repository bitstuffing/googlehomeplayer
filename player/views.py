from django.shortcuts import render

from utils.administrationUtils import AdministrationUtils

def index(request):
    target = "Cocina"
    import pychromecast
    chromecasts = pychromecast.get_chromecasts()
    cast = next(cc for cc in chromecasts if cc.device.friendly_name == target)
    context = {}
    context["device"] = str(cast.device)
    mc = cast.media_controller
    mc.play_media("http://www.hochmuth.com/mp3/Bloch_Prayer.mp3","audio/mp3")
    return AdministrationUtils.render(request,'player/index.html',context)
