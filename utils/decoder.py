import youtube_dl

from urllib.request import urlopen


def decodeUrl(url,audio=True):
    if "youtube." in url:
        ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s'})
        with ydl:
            result = ydl.extract_info(url,download=False)
        if 'formats' in result:
            video = url
            filesize = 0
            for target in result['formats']:
                if target["acodec"] == "opus":
                    if filesize < int(target["filesize"]):
                        video = target["url"]
                elif not audio:
                    video = target["url"]
        else:
            video = result
        return video
    elif "ivoox" in url: #TODOb
        page = urlopen(url)
        #$('.downloadlink').load('downloadlink_mm_30242295_82_b_1.html?tpl2=ok');
        page2 = urlopen(url2)
        #a href="https://www.ivoox.com/esto-es-groove-madrid-leon-19x09-18-11-21-eloy_md_30242295_1.mp3?t=lamjnpWneqepoQ.."
    else:
        return url
