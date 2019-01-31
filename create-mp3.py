#!/usr/bin/env python
# -*- coding: utf-8 -*- 
from __future__ import unicode_literals
from eyed3 import id3

from wordpress_xmlrpc import WordPressPost
from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods import posts, media
from wordpress_xmlrpc.methods.posts import NewPost
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods import taxonomies

import yaml
import os
import glob
import youtube_dl
import sys
import time


# To Fix : URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:841)> in Python

import ssl

ssl._create_default_https_context = ssl._create_unverified_context



os.system("clear")
print("Removing existing mp3 files...")
oldFiles = glob.glob("*.mp3")
for file in oldFiles:
    try:
        os.remove(file)
    except OSError:
        pass

print("Processing the config file...")

audio_info = yaml.load(open('mp3Info.yaml'))

local_file = audio_info['local_file_name']


url = audio_info['youtube_video_url']

if url:

    ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '320',
    }],
    'outtmpl':'%(title)s-%(id)s.%(ext)s'
    }
    print("Downloading YouTube File...")
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        mp3FileName = ydl.prepare_filename(info).replace(info['ext'], 'mp3')

    print("Downloading Completed...")

else:
    mp3FileName = audio_info['local_file_name']


audioTitleInEnglish = audio_info['audio_title_in_english']

title = audio_info['title']

if audio_info['audio_artist']:
    audioArtist = u""+audio_info['audio_artist']
else:
    audioArtist = u"கணியம்" 

if audio_info['audio_album']:
    audioAlbum = u""+audio_info['audio_album']
else:
    audioAlbum = u"கணியம்" 

if audio_info['audio_genre']:
    audioGenre = audio_info['audio_genre']
else:
    audioGenre = "Podcast" 

if audio_info['audio_source_url']:
    audioSourceUrl = audio_info['audio_source_url']
else:
    audioSourceUrl = " " 
    
if audio_info['audio_publisher_url']:
    audioPublisherUrl = audio_info['audio_publisher_url']
else:
    audioPublisherUrl = "http://www.kaniyam.com" 

if audio_info['audio_license']:
    audioLicense = audio_info['audio_license']
else:
    audioLicense = "https://creativecommons.org/licenses/by/4.0/" 

if audio_info['audio_comments']:
    audioComments = audio_info['audio_comments']
else:
    audioComments = "" 

if audio_info['audio_language']:
    audioLang = audio_info['audio_language']
else:
    audioLang = "" 

print("Updating MetaData...")
tag = id3.Tag()
tag.parse(os.path.abspath(mp3FileName))
tag.artist = u""+audioArtist
tag.album = u""+audioAlbum
tag.non_std_genre = u""+audioGenre
tag.title = u""+audioTitleInEnglish
tag.artist_url = b""+bytes(audioSourceUrl,'utf-8')
tag.audio_source_url = b""+bytes(audioSourceUrl,'utf-8')
tag.publisher_url = b""+bytes(audioPublisherUrl,'utf-8')
tag.copyright_url = b""+bytes(audioLicense,'utf-8')
tag.comments.set(u""+audioComments, description=u"")
# read image into memory
imagedata = open(audio_info['audio_art_name'], "rb").read()
# append image to tags
tag.images.set(3, imagedata, "image/jpeg", u"Cover")

tag.save()

print("MetaData updated successfully.....")

timestamp = time.strftime('%Y-%m-%d-%H-%M-%S')
audioTitleInEnglish = audio_info['audio_title_in_english']
ia_identifier = audioTitleInEnglish + "-" + timestamp
os.rename(os.path.abspath(mp3FileName), audioTitleInEnglish + ".mp3")

ia_upload = "ia upload " + ia_identifier + \
    " -m collection:opensource -m mediatype:audio -m sponsor:Kaniyam -m language:ta " + \
    audioTitleInEnglish + ".mp3"

print("Uploading to Internet Archive")
os.system(ia_upload)


audioURL = "https://archive.org/download/%s/%s" % (ia_identifier, audioTitleInEnglish + ".mp3");
print("Uploaded to " + audioURL)

print("Posting into WordPress")

wp_username = audio_info['wp_username']
wp_password = audio_info['wp_password']


wpBlogUrl = audio_info['wp_blog_url']+'/xmlrpc.php'
client = Client(wpBlogUrl, wp_username, wp_password)
post = WordPressPost()

content = "%s \n %s"% (audioURL, audioComments)
post.title = title
post.content = content
post.post_status = 'publish'
post.comment_status = 'open'
post.terms_names = {'category': ['Podcast']}
post.slug = audioTitleInEnglish

if "kaniyam.com" in wpBlogUrl:
    post.post_type =  'podcast'
    post.terms_names = ""
    print("Publishing to Kaniyam")

post.id = client.call(posts.NewPost(post))

print("Posted into WordPress")