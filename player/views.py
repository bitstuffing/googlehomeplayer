from django.shortcuts import render

from django.conf import settings

import pychromecast
from pychromecast import Chromecast, DeviceStatus, CAST_TYPES, CAST_TYPE_CHROMECAST
import json
import base64
import time
import threading
from datetime import datetime
from urllib import request, parse

from utils.administrationUtils import AdministrationUtils

from player.models import Device
from player.models import Status
from player.models import CurrentPlaylist
from player.models import Playlist
from player.models import Track

from utils.decoder import Decoder, Spotify, Youtube

MESSAGE_TYPE = 'type'
TYPE_PAUSE = "PAUSE"

REFRESH_TIME = 0.5
REQUESTED_TIME = 1

WAITING = ["IDLE","LOADING","BUFFERING"]
APPS = ["Spotify","TuneIn Free","Relaxing Sounds","Google News","Google Podcasts"]
PLAYER = "Default Media Receiver"
STABLE = ["PLAYING", "PAUSED", "STOPPED", "UNKNOWN"]

def control(djangoRequest):
    if "reboot" in djangoRequest.POST:
        device = Device.objects.latest("id")
        ip = device.ip_address
        jsonData = {"params":"now"}
        data = '{"params":"now"}'
        url = "http://"+ip+":8008/setup/reboot"
        req =  request.Request(url=url, data=data.encode(),method="POST")
        req.add_header('Content-Type', 'application/json')
        resp = request.urlopen(req)
        return AdministrationUtils.jsonResponse(jsonData)
    elif "kill" in djangoRequest.POST: #just works on chromecast, google home rejects this order
        if Status.objects.count():
            device = Device.objects.latest("id")
            ip = device.ip_address
            status = Status.objects.latest('id')
            app = status.app
            url = "http://"+ip+":8008/apps/"+app
            req =  request.Request(url=url,method="DELETE")
            req.add_header('Content-Type', 'application/json')
            resp = request.urlopen(req)
            return AdministrationUtils.jsonResponse({"kill":app})


def background_process():
    try:
        while settings.RUN:
            print("background is running...")
            #updates related to current
            storedCast = getStoredCast()
            mc = storedCast.media_controller
            time.sleep(REFRESH_TIME)
            if Status.objects.count() == 0:
                status = Status()
            else:
                status = Status.objects.latest('id')
            try:
                status.duration = mc.status.duration
                status.current = mc.status.current_time
                tempState = mc.status.player_state
                if not (tempState == "UNKNOWN" and status.state == "LOADING"):
                    status.state = tempState
                status.volume = storedCast.status.volume_level
                if hasattr(mc.status,"content_id"):
                    status.content = mc.status.content_id
                if hasattr(storedCast.status,"status_text"):
                    status.status_text = storedCast.status.status_text
                status.app = storedCast.status.display_name
                status.save()
                storedCast.socket_client.disconnect()
                storedCast.disconnect()
            except Exception as e:
                print(str(e))
                pass
            #controls player playlist, if it doesn't get inside this condition, it will not order play anything new
            if ((status.state not in WAITING and status.state not in STABLE and status.app == PLAYER) or (status.state in STABLE and status.app != PLAYER) or status.state == "UNKNOWN") and bool(CurrentPlaylist.objects.count()):
                currentPlaylist = CurrentPlaylist.objects.latest('id')
                playlistId = currentPlaylist.playlist_id
                tracks = Track.objects.filter(playlist_id=playlistId).order_by("id")
                found = False
                format = "audio"
                targetTrack = None
                for track in tracks:
                    if currentPlaylist.current_track_id is None:
                        targetTrack = track #save track, needed to metadata info
                        format = track.type
                        currentPlaylist.current_track_id = track.id
                        currentPlaylist.save()
                        status.state = "LOADING"
                        status.save()
                        break
                    elif track.id == currentPlaylist.current_track_id:
                        found = True #indicate next
                    elif found:
                        targetTrack = track #save track, needed to metadata info
                        format = track.type
                        currentPlaylist.current_track_id = track.id
                        currentPlaylist.save()
                        status.state = "LOADING"
                        status.save()
                        break

                if found and targetTrack is None:
                    currentPlaylist.delete()
                if targetTrack is not None:
                    playUrl(targetTrack,format)
            time.sleep(REQUESTED_TIME-REFRESH_TIME) #should be exactly time requested
    except Exception as e:
        settings.RUN = False
        print("Ex:",e)
        pass

def playUrl(track,format):
    finalUrl = track.url
    audio = False
    if format == "audio":
        audio = True

    cast = getStoredCast()
    if finalUrl is not None:
        if ("youtube." in finalUrl or "youtu." in finalUrl ) and not audio:
            audio = False
            from pychromecast.controllers.youtube import YouTubeController
            yt = YouTubeController()
            cast.register_handler(yt)
            finalUrl = finalUrl[finalUrl.rfind("=")+1:]
            yt.play_video(finalUrl)
        else:
            mc = cast.media_controller
            try:
                playerUrl = Decoder.decodeUrl(track,audio)
                decoded = playerUrl
            except Exception as ex:
                print(str(ex))
                playerUrl = finalUrl
                pass
            mc.play_media(playerUrl,format)

def playlist(request):
    if "id" not in request.POST:
        return current_playlist()
    else:
        id = request.POST.get("id")
        if id == "all": #all playlist
            jsonPlaylists = []
            playlists = Playlist.objects.all()
            for playlist in playlists:
                jsonPlaylist = {}
                jsonPlaylist["id"] = playlist.id
                jsonPlaylist["name"] = playlist.name
                jsonPlaylists.append(jsonPlaylist)
            return AdministrationUtils.httpResponse(json.dumps({"playlists": jsonPlaylists}))
        elif "action" not in request.POST: #just one playlist
            jsonTracks = []
            try:
                idNumber = int(id)
                tracks = Track.objects.filter(playlist_id=idNumber).order_by("id")
                for track in tracks:
                    jsonTrack = {}
                    jsonTrack["id"] = track.id
                    jsonTrack["url"] = track.original_url
                    jsonTrack["name"] = track.name
                    jsonTrack["description"] = track.description
                    jsonTrack["creator"] = track.creator
                    jsonTrack["thumbnail"] = track.thumbnail
                    jsonTrack["duration"] = track.duration
                    jsonTracks.append(jsonTrack)
            except Exception as e:
                print("Something goes wrong: "+str(e))
                pass
            return AdministrationUtils.httpResponse(json.dumps({"tracks": jsonTracks}))
        else:
            action = request.POST.get("action")
            response = {}
            response["action"] = action
            if action == "delete":
                obtainedId = request.POST.get("id")
                Playlist.objects.get(id=obtainedId).delete()
                response["id"] = obtainedId
            elif action == "select":
                stop(request)
                obtainedId = request.POST.get("id")
                if CurrentPlaylist.objects.count():
                    CurrentPlaylist.objects.latest('id').delete()
                currentPlaylist = CurrentPlaylist()
                currentPlaylist.device = Device.objects.latest('id').id
                playlist = Playlist.objects.get(id=obtainedId)
                currentPlaylist.playlist = playlist
                currentPlaylist.save()
                response["id"] = obtainedId
            elif action == "edit":
                obtainedId = request.POST.get("id")
                title = request.POST.get("title")
                playlist = Playlist.objects.get(id=obtainedId)
                playlist.name = title
                playlist.save()
            elif action == "import":
                obtainedUrl = request.POST.get("url")
                if "youtu" in obtainedUrl and "list" in obtainedUrl:
                    responseY = Youtube.getPlaylistMetadata(obtainedUrl,list=True)
                    if "entries" in responseY: #import list
                        playlist = Playlist()
                        playlist.name = "Imported playlist"
                        if "title" in responseY:
                            playlist.name = responseY["title"]
                        playlist.save()
                        for entry in responseY["entries"]:
                            track = Track()
                            track.name = entry["title"]
                            track.original_url = "http://youtube.com/watch?v="+entry["url"]
                            track.type = "audio" #TODO
                            track.playlist = playlist
                            track.save()
                        response["added"] = len(responseY["entries"])
                        response["name"] = responseY["title"]
            return AdministrationUtils.jsonResponse(response)

def current_playlist():
    jsonTracks = []
    if CurrentPlaylist.objects.count():
        current = CurrentPlaylist.objects.latest("id")
        tracks = Track.objects.filter(playlist_id = current.playlist_id).order_by("id")
        for track in tracks:
            jsonTrack = {}
            jsonTrack["id"] = track.id
            jsonTrack["url"] = track.original_url
            jsonTrack["name"] = track.name
            jsonTrack["description"] = track.description
            jsonTrack["creator"] = track.creator
            jsonTrack["thumbnail"] = track.thumbnail
            jsonTrack["duration"] = track.duration
            jsonTracks.append(jsonTrack)
    return AdministrationUtils.httpResponse(json.dumps({"tracks": jsonTracks}))

def index(request):
    context = {}
    if Device.objects.count():
        device = Device.objects.latest("id")
        id = device.id
        name = device.friendly_name
        context["id"] = id
        context["name"] = name
        if not settings.RUN:
            settings.RUN = True
            t = threading.Thread(target=background_process, args=(), kwargs={})
            t.setDaemon(True)
            t.start()
    return AdministrationUtils.render(request,'player/index.html',context)

def select_device(request,target):
    chromecasts = pychromecast.get_chromecasts()
    cast = next(cc for cc in chromecasts if cc.device.friendly_name == target)
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
    data = {}
    if "selected" not in request.POST:
        url = request.POST.get("url")
        finalUrl = base64.b64decode(url).decode("utf-8")
        data["playing"] = str(finalUrl)
        isVideo = False
        if "video" in request.POST and request.POST.get("video") == "true":
            isVideo = True
        decode(finalUrl,isVideo)
    else: #selected other playlist track
        selected = request.POST.get("selected")
        track = Track.objects.get(id=selected)
        currentPlaylist = CurrentPlaylist.objects.latest('id')
        currentPlaylist.current_track = track
        currentPlaylist.save()
        format = track.type
        pause(request)
        playUrl(track,format)
    return AdministrationUtils.httpResponse(json.dumps(data))

def decode(finalUrl,isVideo):
    if CurrentPlaylist.objects.count()==0: #creating new playlist
        currentPlaylist = CurrentPlaylist()
        currentPlaylist.device = Device.objects.latest('id').id
        random = False
        playlist = Playlist()
        playlist.name = "New playlist"
        playlist.save()
    else: #use last playlist to append tracks
        currentPlaylist = CurrentPlaylist.objects.latest('id')
        playlist = Playlist.objects.get(id=currentPlaylist.playlist_id)
    track = Track()
    track.name = "Dummy track name"
    track.original_url = finalUrl
    track.type = "audio"
    track.playlist_id = playlist.id
    if isVideo:
        track.type = "video"
    track.save()
    #select playlist in current playlists
    if CurrentPlaylist.objects.count()==0:
        currentPlaylist.playlist = playlist
        currentPlaylist.save()

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
    if CurrentPlaylist.objects.count():
        CurrentPlaylist.objects.latest('id').delete()
        print("stop has deleted current playlist!")
    if Status.objects.count() == 0:
        status = Status()
    else:
        status = Status.objects.latest('id')
    status.state = "STOPPED" #stopped
    status.save()
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
    cast.set_volume(vol)
    cast.wait()
    return AdministrationUtils.httpResponse(str(cast))

def track(request):
    storedStatus = Status.objects.latest('id')
    status = {}
    if storedStatus.state == "PLAYING":
        current = storedStatus.updated.timestamp()
        now = datetime.now().timestamp()
        difference = now - current
    else:
        difference = 0
    status["duration"] = storedStatus.duration
    status["current"] = difference + storedStatus.current
    status["state"] = storedStatus.state
    status["volume"] = storedStatus.volume
    status["content"] = storedStatus.content
    status["app"] = storedStatus.app

    if CurrentPlaylist.objects.count():
        currentPlaylist = CurrentPlaylist.objects.latest("id")
        if (currentPlaylist.current_track is not None and (storedStatus.app is None or storedStatus.app in APPS) and (storedStatus.state == "UNKNOWN" or storedStatus.state == "IDLE")) or (storedStatus.state not in WAITING and storedStatus.state not in STABLE and storedStatus.app != PLAYER): #apps have the control
            currentPlaylist.delete()
            print("track has deleted current playlist: "+storedStatus.state)
        else: #you have the control
            track = currentPlaylist.current_track
            if track is not None:
                status["track_name"] = track.name
                status["track_id"] = track.id
                status["track_url"] = track.original_url
    elif storedStatus.app == "Spotify" and "spotify:" in storedStatus.content:
        status["track_name"] = Spotify.getMetadata(storedStatus.content) #translates spotify code to right metadata
    elif storedStatus.app is not None and storedStatus.app in APPS:
        status["track_name"] = storedStatus.content
        status["track_text"] = storedStatus.status_text
    return AdministrationUtils.jsonResponse(status)

def getStoredCast(request = None):
    if request is not None:
        try:
            integerId = int(request.POST.get("id"))
            device = Device.objects.get(id=integerId)
        except:
            device = Device.objects.latest('id')
            pass
    else:
        device = Device.objects.latest('id')
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
