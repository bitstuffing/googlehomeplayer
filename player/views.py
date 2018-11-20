from django.shortcuts import render

from utils.administrationUtils import AdministrationUtils

def index(request):
    context = {}
    return AdministrationUtils.render(request,'player/index.html',context)
