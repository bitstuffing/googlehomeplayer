from django.shortcuts import render

from utils.administrationUtils import AdministrationUtils

def index(request):
    target = "Cocina"
    import pychromecast
    chromecasts = pychromecast.get_chromecasts()
    cast = next(cc for cc in chromecasts if cc.device.friendly_name == target)
    context = {}
    context["device"] = str(cast.device)
    print(str(context))
    return AdministrationUtils.render(request,'player/index.html',context)
