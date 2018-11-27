import youtube_dl

from urllib.request import urlopen


def extract(fromString, toString, data):
    newData = data[data.find(fromString) + len(fromString):]
    newData = newData[0:newData.find(toString)]
    return newData


def rExtract(fromString, toString, data):
    newData = data[0:data.rfind(toString)]
    newData = newData[newData.rfind(fromString) + len(fromString):]
    return newData


def extractWithRegex(fromString, toString, data):
    newData = data[data.find(fromString):]
    newData = newData[0:newData.find(toString) + len(toString)]
    return newData


def rExtractWithRegex(fromString, toString, data):
    newData = data[0:data.rfind(toString) + len(toString)]
    newData = newData[newData.rfind(fromString):]
    return newData


def decodeUrl(url,audio=True):
    if "ivoox.com" in url: #TODOb
        page = urlopen(url).read().decode('utf-8')
        url2 = "https://www.ivoox.com/"+extract("$('.downloadlink').load('","'",str(page))
        page = urlopen(url2).read().decode('utf-8')
        finalUrl = "https://www.ivoox.com/"+extract('a href="https://www.ivoox.com/','"',str(page))
        return finalUrl
    else:
        try:
            ydl = youtube_dl.YoutubeDL({
                'socket_timeout': 10,
            })
            with ydl:
                result = ydl.extract_info(url,download=False)
            if 'formats' in result:
                video = url
                filesize = 0
                try:
                    print("hello!")
                    for target in result['formats']:
                        if audio:
                            if "acodec" in target and target["acodec"] == "opus" and filesize < int(target["filesize"]):
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
            else:
                video = result
            return video
        except Exception as e:
            print("Ex: "+str(e))
            pass
    return url
