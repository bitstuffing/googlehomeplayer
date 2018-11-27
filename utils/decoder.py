import youtube_dl

from urllib.request import urlopen


def decodeUrl(url,audio=True):
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
                    print(str(target))
                    if audio:
                        print("0")
                        if "acodec" in target and target["acodec"] == "opus" and filesize < int(target["filesize"]):
                            print("a")
                            video = target["url"]
                            filesize = int(target["filesize"])
                    elif not audio :
                        if "filesize" in target:
                            if filesize < int(target["filesize"]):
                                print(str(target))
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
        print("ex: "+str(e))
        pass
    #elif "ivoox" in url: #TODOb
    #    page = urlopen(url)
        #$('.downloadlink').load('downloadlink_mm_30242295_82_b_1.html?tpl2=ok');
    #    page2 = urlopen(url2)
        #a href="https://www.ivoox.com/esto-es-groove-madrid-leon-19x09-18-11-21-eloy_md_30242295_1.mp3?t=lamjnpWneqepoQ.."
    #else:
    #    return url
