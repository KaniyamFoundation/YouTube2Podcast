#!/usr/bin/env python
# -*- coding: utf-8 -*- 
from __future__ import unicode_literals
from eyed3 import id3
import yaml
import os
import eyed3
import glob
import youtube_dl


os.system("clear")
print(".....Removing existing mp3 files.....")
oldFiles = glob.glob("*.mp3")
for file in oldFiles:
    try:
        os.remove(file)
    except OSError:
        pass
print("....Processing the config file....")

book_info = yaml.load(open('mp3Info.yaml'))
print("...Downloading YouTube File...")
url = "https://www.youtube.com/watch?v=%s" %book_info['youtube_video_id']

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '320',
    }],
    'outtmpl':'%(title)s-%(id)s.%(ext)s'
}
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(url, download=True)
    mp3FileName = ydl.prepare_filename(info).replace(info['ext'], 'mp3')

print("..Downloading Completed.."+mp3FileName)

if book_info['audio_artist']:
    audioArtist = u""+book_info['audio_artist']
else:
    audioArtist = u"கணியம்" 

if book_info['audio_album']:
    audioAlbum = u""+book_info['audio_album']
else:
    audioAlbum = u"கணியம்" 

if book_info['audio_genre']:
    audioGenre = book_info['audio_genre']
else:
    audioGenre = "Podcast" 

if book_info['audio_source_url']:
    audioSourceUrl = book_info['audio_source_url']
else:
    audioSourceUrl = " " 
    
if book_info['audio_publisher_url']:
    audioPublisherUrl = book_info['audio_publisher_url']
else:
    audioPublisherUrl = "http://www.kaniyam.com" 

if book_info['audio_license']:
    audioLicense = book_info['audio_license']
else:
    audioLicense = "https://creativecommons.org/licenses/by/4.0/" 

if book_info['audio_comments']:
    audioComments = book_info['audio_comments']
else:
    audioComments = "" 

if book_info['audio_language']:
    audioLang = book_info['audio_language']
else:
    audioLang = "" 

print(".....Updating MetaData.....")
tag = id3.Tag()
tag.parse(os.path.abspath(mp3FileName))
tag.artist = u""+audioArtist
tag.album = u""+audioAlbum
tag.non_std_genre = u""+audioGenre
tag.title = u""+info['title']
tag.artist_url = b""+audioSourceUrl
tag.audio_source_url = b""+str(url)
tag.publisher_url = b""+audioPublisherUrl
tag.copyright_url = b""+audioLicense
tag.comments.set(u""+audioComments, description=u"", lang=audioLang)
# read image into memory
imagedata = open(book_info['audio_art_name'], "rb").read()
# append image to tags
tag.images.set(3, imagedata, "image/jpeg", u"Cover")

tag.save()

print(".....Completed.....")