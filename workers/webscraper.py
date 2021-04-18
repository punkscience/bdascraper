
from PySide2.QtCore import *
from PySide2.QtGui import *
import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, unquote
import requests
import json
from datetime import datetime

class ScraperThread(QThread):

    scraper_complete = Signal(object)
    scraper_update = Signal(object)

    def __init__(self, rootUrl ):
        QThread.__init__(self)
        self.rootUrl = rootUrl

    def parseFolder( self, sub, nightFolder ):
        url = urljoin( sub, nightFolder )
        #print( "Scanning " + url + '...') 
        pagecontent = requests.get( url, headers={"User-Agent": "XY"})
        soup = BeautifulSoup( pagecontent.content, "html.parser")

        anchors = soup.find_all('a')

        for anchor in anchors:
            
            localAnchor = anchor['href']
            contents = anchor.contents[0]
            if contents.find( 'Parent') != -1:
                continue

            if localAnchor != "/" and localAnchor[len(localAnchor)-1] == '/' and localAnchor.find('http://') == -1 and localAnchor.find('https://') == -1:
                self.parseFolder( url, localAnchor )
            elif localAnchor.find( '.mp3' ) != -1:
                mp3url = urljoin( url, localAnchor )
                
                urlObj = urlparse( mp3url )
                filename = os.path.basename(urlObj.path)
                filename = unquote( filename )

                obj = {
                    'event': unquote( nightFolder ).replace( '/', ''),
                    "url": mp3url,
                    "filename": filename,
                    "downloaded": False
                }
                
                self.db['files'].append( obj )
                self.scraper_update.emit( obj )

    def run(self):
        
        # Create a local database
        self.db = {
            "output": "",
            "last_scan": datetime.now().isoformat(),
            "files": []
        }

        # Parse the web
        self.parseFolder( self.rootUrl, '')

        self.scraper_complete.emit( self.db )
        
