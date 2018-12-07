from django.shortcuts import render

from django.conf import settings

import pychromecast
from pychromecast import Chromecast, DeviceStatus, CAST_TYPES, CAST_TYPE_CHROMECAST
import json
import base64
import time
import threading
from datetime import datetime

from utils.administrationUtils import AdministrationUtils

from player.models import Device
from player.models import Status
from player.models import CurrentPlaylist
from player.models import Playlist
from player.models import Track

from utils.decoder import Decoder, Spotify

MESSAGE_TYPE = 'type'
TYPE_PAUSE = "PAUSE"

REFRESH_TIME = 0.5
REQUESTED_TIME = 1

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
                status.content = mc.status.content_id
                status.app = storedCast.status.display_name
                status.save()
                #storedCast.socket_client.socket.close()
                storedCast.socket_client.disconnect()
                storedCast.disconnect()
            except Exception as e:
                print(str(e))
                pass
            #controls player playlist
            if status.state != "IDLE" and status.state != "PLAYING" and status.state != "PAUSED" and status.state != "LOADING" and status.state != "BUFFERING" and CurrentPlaylist.objects.count():
                #check if there is an active playlist and if there are tracks
                print("checking..."+str(status.state))
                currentPlaylist = CurrentPlaylist.objects.latest('id')
                playlistId = currentPlaylist.playlist_id
                tracks = Track.objects.filter(playlist_id=playlistId).order_by("id")
                finalUrl = None
                found = False
                format = "audio"
                targetTrack = None
                for track in tracks:
                    targetUrl = track.original_url
                    print("checking: "+targetUrl+", id: "+str(track.id))
                    if currentPlaylist.current_track_id is None:
                        print("a")
                        finalUrl = targetUrl
                        targetTrack = track #save track, needed to metadata info
                        format = track.type
                        currentPlaylist.current_track_id = track.id
                        currentPlaylist.save()
                        status.state = "LOADING"
                        status.save()
                        break
                    elif track.id == currentPlaylist.current_track_id:
                        print("b")
                        found = True #indicate next
                    elif found:
                        print("c")
                        finalUrl = targetUrl
                        targetTrack = track #save track, needed to metadata info
                        format = track.type
                        currentPlaylist.current_track_id = track.id
                        currentPlaylist.save()
                        status.state = "LOADING"
                        status.save()
                        break
                    else:
                        print("d")

                if found and finalUrl is None:
                    currentPlaylist.delete()

                playUrl(track,format)

            time.sleep(REQUESTED_TIME-REFRESH_TIME) #should be exactly time requested
    except Exception as e:
        settings.RUN = False
        print("Ex:",e)
        pass
    print("background has finished")

def playUrl(track,format):
    finalUrl = track.url
    audio = False
    if format == "audio":
        audio = True

    cast = getStoredCast()
    if finalUrl is not None:
        print("trying to play: "+finalUrl)
        if ("youtube." in finalUrl or "youtu." in finalUrl ) and not audio:
            print("youtube app...")
            audio = False
            from pychromecast.controllers.youtube import YouTubeController
            yt = YouTubeController()
            cast.register_handler(yt)
            finalUrl = finalUrl[finalUrl.rfind("=")+1:]
            yt.play_video(finalUrl)
        else:
            print("decoder part...")
            mc = cast.media_controller
            try:
                playerUrl = Decoder.decodeUrl(targetTrack,audio)
                print("decoder has returned: "+playerUrl)
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
        playUrl(track,format)
    return AdministrationUtils.httpResponse(json.dumps(data))

def decode(finalUrl,isVideo):
    if CurrentPlaylist.objects.count()==0:
        print("Creating a new playlist (1)")
        currentPlaylist = CurrentPlaylist()
        currentPlaylist.device = Device.objects.latest('id').id
        random = False
        playlist = Playlist()
        playlist.name = "New playlist"
        playlist.save()
    else:
        print("Using current playlist (2)")
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
    if Status.objects.count() == 0:
        status = Status()
    else:
        status = Status.objects.latest('id')
    status.state = "UNKNOWN" #stopped
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
        if storedStatus.app == "Spotify": #spotify app has the control
            currentPlaylist.delete()
        else: #you have the control
            track = currentPlaylist.current_track
            status["track_name"] = track.name
            status["track_id"] = track.id
            status["track_url"] = track.original_url
    elif storedStatus.app == "Spotify":
        status["track_name"] = Spotify.getMetadata(storedStatus.content)

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
