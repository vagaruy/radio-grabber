import socket
import sys
import time
import os
import urllib2
import contextlib
import sqlite3
import re
import string



DATABASE = '/codes/radio/radiostream.db'
link = ''
		

def insert_song(song_stream):
	print song_stream
	
	connection=sqlite3.connect(DATABASE)
	
	with connection:
		cursor=connection.cursor()
		
		print cursor.execute('INSERT OR IGNORE INTO Songs VALUES (?, ?,?)',song_stream)
				
    
def parse_headers(response):
	headers = {}
	while True:
		line = response.readline()
		
		if line == '\r\n':
			break # end of headers
		
		if ':' in line:
			key, value = line.split(':', 1)
			headers[key] = value
	return headers
	
def parse_flv_meta(response):
	song=''
	flv_line=response.readline()
	if flv_line.find("FLV")!=-1:			#CONTAINS THE FLV HEADER WHICH MIGHT INDICATE WE HAVE SOMETHING
		response.readline()
		response.readline()
		response.readline()
		
		imp_line=response.readline()			
		
		l_index=imp_line.find('Artist')+6   #parsing in format Artist - Song
		r_index=imp_line.find('BuyNowURL')
		if l_index!=-1 and r_index!=-1:
			song=imp_line[l_index:r_index]
		
		l_index=imp_line.find('Title')+5
		r_index=imp_line.find('Type')
		if l_index!=-1 and r_index!=-1:
			song=song+'-'+imp_line[l_index:r_index]
			
		song=filter(lambda x: x in string.printable,song)  #removing weird shit
		song=" ".join(song.split())
		song_stream=((str(song),str(link)))
		
		
	return song_stream
	
def parse_icy_meta(response):

	headers = parse_headers(response)	
	meta_interval = int(headers['icy-metaint'])
	response.read(meta_interval) # throw away the data until the meta interval

	length = ord(response.read(1)) * 16 # length is encoded in the stream
	metadata = response.read(length)
	

	l_index=metadata.find('=')+2
	#print "left index", l_index
	
	r_index=metadata.find('\';')
	#print 'right index', r_index
	song=metadata[l_index:r_index]
	
	l_index=r_index+13
	r_index=metadata.rfind('\';')
	stream=metadata[l_index:r_index]
	song_stream=((song,stream))
	
	return song_stream
		

def parse_meta(response):
	
	if 'Content-Type' not in response.info():			#checking the content type  if it even exists or not Icecast has no http header in info() have to parse 
		song_stream=parse_icy_meta(response)			#nothing in content type...header might  possibly  be not there or could be a icecast stream.
	elif response.info()['Content-type']=='application/flv':	#can assume it to be a flv stream 
		song_stream=parse_flv_meta(response)
	else:
                
		song_stream=(("",""))
	return (song_stream)
		

		
def poll_radio(stream="http://8313.live.streamtheworld.com/WPOIFMAAC"):
	global link
	link=stream
	request = urllib2.Request(stream, headers = {'User-Agent' : 'User-Agent: VLC/2.0.5 LibVLC/2.0.5','Icy-MetaData' : '1','Range' : 'bytes=0-',})
    # the connection will be close on exit from with block
	with contextlib.closing(urllib2.urlopen(request)) as response:
			
		song_stream=parse_meta(response)
		
	return song_stream
		
def run_stations():
	try:
		station_con = sqlite3.connect(DATABASE)
		with station_con:    
		
			station_cur = station_con.cursor()   
			station_rows=station_cur.execute("SELECT station FROM Stations")
			rows=station_rows.fetchall()
			for row in rows:
				#print row[0]
				song_stream=poll_radio(row[0])
				song_stream=song_stream+(0,)
				insert_song(song_stream)
				#print song_stream
	except:
		pass
		
def hours_run(hours):
	
	while hours>0:
		run_stations()
		time.sleep(120)
		hours-=1
	
				
	
try:
	hours_run(10000)
except:	
	pass
	
	

