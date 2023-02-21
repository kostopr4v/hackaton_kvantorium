from __future__ import unicode_literals
import os
import urllib.request
import re
from youtubesearchpython import *
from pytube import YouTube


def toyt(sors):
    customSearch = CustomSearch(sors, VideoSortOrder.viewCount, limit=1)
    link = customSearch.result()["result"][0]["link"]

    try:
        url = link
        # качается
        yt = YouTube(url)
        video = yt.streams.get_audio_only()
        base1, ext1 = os.path.splitext(video.default_filename)
        if (base1 + ".mp3") not in os.listdir("data/"):
            k = video.download("data/")
            base, ext = os.path.splitext(k)
            new_file = base + '.mp3'
            os.rename(k, new_file)
            return base.split("/")[-1]
        return False
    except:
        pass
