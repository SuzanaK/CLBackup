#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib, urllib2, sys, os, time, simplejson, codecs
from PyQt4 import QtGui, QtCore
import exiting

API_URL_PAL = 'http://www.colourlovers.com/api/palettes/'
API_URL_PAT = 'http://www.colourlovers.com/api/patterns/'

# how long to wait between one image and the next
#SLEEP_TIME = 0.5 # seconds


class Downloader (QtCore.QObject):


    def __init__(self):
        super(Downloader, self).__init__()

    def download_image(self, directory, title, image_url):

        if exiting.exiting: return 
        
        title = "".join(i for i in title if i not in "\/:*?<>|")
        #if os.path.isdir(directory):
        filename = directory + os.sep +  title + '.png'
        #else:
            #filename = title + '.png'
        try: 
            urllib.urlretrieve(image_url, filename)
        except: 
            self.emit(QtCore.SIGNAL('update(QString)'), "ERROR - Could not download image. Please check your internet connection!" )
            
        self.emit(QtCore.SIGNAL('update(QString)'), "Downloaded image file %s"%filename)


    def download_palette_colors(self, directory, title, colors, date):

        if exiting.exiting: return 
        title = "".join(i for i in title if i not in "\/:*?<>|")
        if os.path.isdir(directory):
            filename = directory + os.sep +  title + '.txt'
        else:
            filename = title + '.txt'
	    
        try: 
            fh = codecs.open(filename, mode="w", encoding="utf-8")
            fh.write(title + " - created on %s\n\n"%date)
            fh.write(", ".join(colors))
            fh.close() 
        except: 
            self.emit(QtCore.SIGNAL('update(QString)'), "ERROR - Could not save color text file. Do you have writing rights in directory %s ?" %directory)

    def download_palettes(self, username, dir_pal):
     
        offset = 0
        while True: 
            if exiting.exiting: return
            data = {'lover':username,'format':'json','resultOffset':str(offset),'numResults':'100'}
            data_encoded = urllib.urlencode(data)
            request = urllib2.Request(API_URL_PAL, data_encoded, headers={'User-Agent':'Saving the love'})

            try:
                fh = urllib2.urlopen(request)
                data = simplejson.load(fh)
                if len(data) == 0:
                    self.emit( QtCore.SIGNAL('update(QString)'), "ERROR - No palettes found for %s!"%username)
                    return 
            except: 
                self.emit(QtCore.SIGNAL('update(QString)'), "ERROR - Could not connect to the CL API. Please check your internet connection!") 
                return 

            self.emit(QtCore.SIGNAL('update(QString)'), "Received a list with the next %d palettes."%len(data))

            for i in data:
                if exiting.exiting: return
                image_url = i['imageUrl']
                title = i['title']
                colors = i['colors']
                date = i['dateCreated']
                self.download_palette_colors(dir_pal, title, colors, date)
                self.download_image(dir_pal, title, image_url)
                # in case that ColourLovers will block your IP when there are too many requests in a short time
                # time.sleep(SLEEP_TIME)
                      
            if len(data) < 100:
                break
            offset += len(data)
            # The API will break silently when trying to download more than 1000 palettes or patterns :-( 
            if offset >= 1000:
                break


    def download_patterns(self, username, dir_pat):    

        offset = 0
        while True: 
            if exiting.exiting: return
            data = {'lover':username,'format':'json','resultOffset':str(offset),'numResults':'100'}
            data_encoded = urllib.urlencode(data)
            request = urllib2.Request(API_URL_PAT, data_encoded, headers={'User-Agent':'ColourLovers Browser'})
            try:
                fh = urllib2.urlopen(request)
                data = simplejson.load(fh)
                if len(data) == 0:
                    self.emit( QtCore.SIGNAL('update(QString)'), "ERROR - No patterns found for %s!"%username)
                    return 
            except: 
                return "ERROR - Could not connect to the CL API. Please check your internet connection!" 
                return 

            self.emit(QtCore.SIGNAL('update(QString)'), "Received a list with the next %d patterns."%len(data))

            for i in data:
                if exiting.exiting: return 
                image_url = i['imageUrl']
                badge_url = i['badgeUrl'] 
                title = i['title']
                self.download_image(dir_pat, title, image_url)
                self.download_image(dir_pat, title + "_badge", badge_url)
                # in case that ColourLovers will block your IP when there are too many requests in a short time
                # time.sleep(SLEEP_TIME)
                      
            if len(data) < 100:
                break
            offset += len(data)
            # The API will break silently when trying to download more than 1000 palettes or patterns :-( 
            if offset >= 1000:
                break







