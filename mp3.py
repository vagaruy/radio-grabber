import socket
import sys
import time
import os
import urllib2
import contextlib
import sqlite3
import re
from HTMLParser import HTMLParser
from bs4 import BeautifulSoup

DATABASE = 'radiostream.db'

def result_parser(webpage):

	l_index=webpage.find('results-list')
	r_index=webpage.find('/ol')
	#print l_index,r_indexsudo
	return webpage[l_index:r_index]
		
def poll_radio(stream,song_name,connection):
	request = urllib2.Request(stream)
    # the connection will be close on exit from with block
	with contextlib.closing(urllib2.urlopen(request)) as response:

		#headers = parse_headers(response
		#print response.info()
		metadata = response.read()
		
	soup=BeautifulSoup(metadata)
	try:
		count=len(soup.ol)
		#print "Amount of data is ", count
		counter=1
		while counter<count:
			song_info=parse_info( soup.ol.contents[counter].get_text(),soup.ol.contents[counter].a.get('href'),song_name)
			insert_db(song_info,connection)
			counter+=2
			if counter>8:
				break
	except:
		pass
	
def insert_db(song_info,con_songlink):
	#con_songlink=sqlite3.connect(DATABASE)
	#with con_songlink:
	cur=con_songlink.cursor()
	cur.execute('INSERT INTO SongLink VALUES (?, ?,?, ?,?, ?,?, ?,?,?)',song_info)
	con_songlink.commit()
	
	
def parse_info(info,link,song_name):
	#print info
	
	# Database schema as follows
	#CREATE TABLE SongLink(File TEXT,Song TEXT,Artist TEXT,Album TEXT,Genre TEXT,Duration TEXT,Bitrate TEXT,Domain TEXT,Beeid TEXT,Dlink TEXT);
	song_info=[]
	l_index=info.find('File name')+11
	r_index=info[l_index:].find('\n')+l_index
	song_info.append(info[l_index:r_index])		#append file name
	
	song_info.append(song_name)				#append Song
	#print  "FileName:",info[l_index:r_index]
	l_index=info[r_index:].find('Artist')+8+r_index
	r_index=info[l_index:].find('Album')+l_index
	song_info.append(info[l_index:r_index-1].rstrip(' \n\r\t'))			#append Artist
	#print  "Artist", info[l_index:r_index-1]
	l_index=info[r_index:].find('Album')+7+r_index
	r_index=info[l_index:].find('Genre')+l_index
	song_info.append(info[l_index:r_index-1].rstrip(' \n\r\t'))				#append Albunm
	#print "Album", info[l_index:r_index-1]
	l_index=info[r_index:].find('Genre')+7+r_index
	r_index=info[l_index:].find('Year')+l_index
	song_info.append(info[l_index:r_index-1].rstrip(' \n\r\t'))				#append Genre
	#print "Genre", info[l_index:r_index-1]
	l_index=info[r_index:].find('Duration')+10+r_index
	r_index=info[l_index:].find('Bitrate')+l_index
	song_info.append(info[l_index:r_index-2].rstrip(' \n\r\t'))		
	#print "Duration", info[l_index:r_index-1]			#append duration
	l_index=info[r_index:].find('Bitrate')+9+r_index
	r_index=info[l_index:].find('Frequency')+l_index
	song_info.append(info[l_index:r_index-1].rstrip(' \n\r\t'))				#append Bitrate
	#print "Bitrate", info[l_index:r_index-1]
	l_index=info[r_index:].find('Domain')+8+r_index
	r_index=info[l_index:].find('\n')+l_index
	song_info.append(info[l_index:r_index].rstrip(' \n\r\t'))				#append Domain
	#print "Domain", info[l_index:r_index]
	l_index=link.find('file')
	r_index=link.find('&')
	song_info.append( link[l_index+5:r_index].rstrip(' \n\r\t'))		#append beeId
	song_info.append('')
	print song_info
	return song_info
	
	
	
	
	
	
		
def search_songs():
	connection=sqlite3.connect(DATABASE)
	with connection:
		cursor=connection.cursor()
		option=cursor.execute('select Songs.Song from Songs LEFT JOIN SongLink	ON Songs.Song= SongLink.Song WHERE SongLink.Song IS NULL AND Songs.Stream=\"http://www.buddharadio.com\"')
		#option=cursor.execute('SELECT Songs.Song FROM Songs,SongLink WHERE Songs.Song!=SongLink.Song AND Songs.Stream=\"http://www.buddharadio.com\"')
		
		for i in option: 
			song_name=i[0]
			#print song_name[0]
			song_url=song_name.replace(' ','+')
			song_url="http://beemp3.com/index.php?q="+song_url+"&st=all:80"
			#print song_name
			poll_radio(song_url,song_name,connection)
			time.sleep(3)
			
search_songs()