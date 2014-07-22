from apiclient.discovery import build
from optparse import OptionParser

# Set DEVELOPER_KEY to the "API key" value from the "Access" tab of the
# Google APIs Console http://code.google.com/apis/console#access
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = "AIzaSyDGkjc-HvC4uCWPL5qVNdQGLXunik-liqw"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

import socket
import sys
import time
import os
import urllib2
import contextlib
import subprocess

def find_size(you_url):

	args=['sudo','youtube-dl','-s','-g']
	you_url='http://www.youtube.com/watch?v='+str(you_url)
        args.append(you_url)
        
	#print args
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        
        #for line in p.stdout.readlines():
        #       print (line)
        #       i+=1
        #print "number of lines is", i
        stream= p.stdout.readline()
        #print stream

        request = urllib2.Request(stream)
        with contextlib.closing(urllib2.urlopen(request)) as response:
                bytes_len=int(  response.info().getheader('Content-Length'))
                bytes_len=((bytes_len)/(1024*1024))
                return (int( bytes_len) )

def youtube_search(options):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  search_response = youtube.search().list(
    q=options.q,
    part="id",
    maxResults=options.maxResults
  ).execute()

  videos = []
  
  for search_result in search_response.get("items", []):
    if search_result["id"]["kind"] == "youtube#video":
      videoId= (search_result["id"]["videoId"])
      bytes=find_size(videoId)
      videos.append([bytes,videoId])

  videos=sorted(videos)
  print videos
    
 # print "Videos:\n", "\n".join(videos), "\n"
  


if __name__ == "__main__":
  parser = OptionParser()
  parser.add_option("--q", dest="q", help="Search term",
    default="Swedish House Mafia Don't you Worry Child")
  parser.add_option("--max-results", dest="maxResults",
    help="Max results", default=5)
  (options, args) = parser.parse_args()

  youtube_search(options)
