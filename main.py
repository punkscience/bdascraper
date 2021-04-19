import os
import json
from datetime import datetime, timedelta
import logging

from workers.webscraper import ScraperThread


ROOTURL = 'http://archives.bassdrivearchive.com/'
DBFILE = 'filedata.json'
DEBUG = True

gProcessVars = {
    'scrape_thread': None,
    'db': None
}

  
def startWebScraping( rootUrl ):
    logging.info("Starting web scraping from {}...".format(rootUrl))
    gProcessVars['scrape_thread'] = ScraperThread(rootUrl, onScraperUpdate, onScraperComplete )
    gProcessVars['scrape_thread'].start()
    
def onScraperUpdate( obj ):
    pass
        
def onScraperComplete( newdb ):
    for obj in newdb['files']:
        if obj not in gProcessVars['db']['files']:
            gProcessVars['db']['files'].append(obj)
            logging.info("Adding new mix: {}".format(obj['filename']))

    gProcessVars['db']['last_scan'] = datetime.now().isoformat()

    # Dump out the results 
    with open( DBFILE, "w" ) as f:
        json.dump(gProcessVars['db'], f, indent=4)

    logging.info("Completed scraping.")

def writeDb( self ):
    gProcessVars['db']['output'] = ''
    with open( DBFILE, "w") as f:
        json.dump( self.db, f, indent=4)        


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    # Read in what we've already scanned
    if os.path.isfile(DBFILE):
        with open(DBFILE, "r") as f:
            gProcessVars['db'] = json.load(f)
    else:
        gProcessVars['db'] = {
            "last_scan": "2020-01-28T19:19:10.702353",
            "files": []
        }

    logging.info('Last scrape was {}'.format(gProcessVars['db']['last_scan'] ))

    okToScrape = datetime.now() >= datetime.fromisoformat(
        gProcessVars['db']['last_scan']) + timedelta(hours=12)
    if DEBUG == True or okToScrape == True:
        startWebScraping(ROOTURL)
    else:
        logging.info("Nothing to scrape.")




