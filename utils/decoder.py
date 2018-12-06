import youtube_dl

from urllib.request import urlopen

class Decoder():

    @staticmethod
    def extract(fromString, toString, data):
        newData = data[data.find(fromString) + len(fromString):]
        newData = newData[0:newData.find(toString)]
        return newData

    @staticmethod
    def rExtract(fromString, toString, data):
        newData = data[0:data.rfind(toString)]
        newData = newData[newData.rfind(fromString) + len(fromString):]
        return newData

    @staticmethod
    def extractWithRegex(fromString, toString, data):
        newData = data[data.find(fromString):]
        newData = newData[0:newData.find(toString) + len(toString)]
        return newData

    @staticmethod
    def rExtractWithRegex(fromString, toString, data):
        newData = data[0:data.rfind(toString) + len(toString)]
        newData = newData[newData.rfind(fromString):]
        return newData

    @staticmethod
    def decodeUrl(track,audio=True):
        url = track.original_url
        if "ivoox.com" in url: #TODO
            track = Ivoox.decode(track)
            track.save()
            url = track.url
        else:
            track = Youtube.decode(track,audio)
            url = track.url
            if url is None or url == "":
                url = track.original_url
            print("target url is: "+str(url))
        return url


class Youtube():

    @staticmethod
    def decode(track,audio=True):
        try:
            url = track.original_url
            ydl = youtube_dl.YoutubeDL({
                'socket_timeout': 10,
            })
            with ydl:
                result = ydl.extract_info(url,download=False)
            filesize = 0
            track.creator = result["creator"]
            track.name = result["title"]
            track.thumbnail = result["thumbnail"]
            track.description = result["description"]
            track.duration = result["duration"]
            if 'formats' in result:
                video = url
                try:
                    for target in result['formats']:
                        if audio:
                            if "acodec" in target and (target["acodec"] == "opus" or "mp4a" in target["acodec"]) and filesize < int(target["filesize"]):
                                video = target["url"]
                                filesize = int(target["filesize"])
                        elif not audio :
                            if "filesize" in target:
                                if filesize < int(target["filesize"]):
                                    video = target["url"]
                                    filesize = int(target["filesize"])
                            else:
                                video = target["url"]
                except Exception as ex:
                    print("Exception: "+str(ex))
                    pass
                track.url = video
                track.save()
            else:
                print("it's not a youtube track, metadata not found!")
        except Exception as e:
            print("Ex: "+str(e))
            pass
        return track


class Ivoox():

    @staticmethod
    def decode(track):
        url = track.original_url
        page = urlopen(url).read().decode('utf-8')
        track.description = Decoder.extract('<meta property="og:description" content="','"',page)
        track.name = Decoder.extract('<meta property="og:title" content="','"',page)
        track.thumbnail = Decoder.extract('<meta property="og:image" content="','"',page)
        duration = Decoder.extract("var audio_duration  = '","'",page)
        #duration is in format 00:00:00
        finalDuration = 0
        if ":" in duration:
            times = duration.split(":")
            if len(times) == 2:
                finalDuration = int(times[0])*60+int(times[1])
            else: #len is 3
                finalDuration = int(times[0])*3600+int(times[1])*60+int(times[2])
        else:
            try:
                finalDuration = int(duration)
            except:
                print("unknown format, skipping...")
                pass
        track.duration = finalDuration
        url2 = "https://www.ivoox.com/"+Decoder.extract("$('.downloadlink').load('","'",str(page))
        page = urlopen(url2).read().decode('utf-8')
        finalUrl = "https://www.ivoox.com/"+Decoder.extract('a href="https://www.ivoox.com/','"',str(page))
        track.url = finalUrl
        return track
