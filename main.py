import os
import json
from datetime import datetime, timedelta
import logging
import argparse
#from apscheduler.schedulers import BlockingScheduler 

from workers.webscraper import ScraperThread


ROOTURL = 'http://archives.bassdrivearchive.com/'
DBFILE = 'filedata.json'
DEBUG = False

gProcessVars = {
    'scrape_thread': None,
    'db': None,
    'hours': 0
}

# sched = BlockingScheduler()
# sched.start()

  
def startWebScraping( rootUrl ):
    logging.info("Starting web scraping from {}...".format(rootUrl))
    gProcessVars['scrape_thread'] = ScraperThread(rootUrl, onScraperUpdate, onScraperComplete )
    gProcessVars['scrape_thread'].start()
    gProcessVars['scrape_thread'].join()
    
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
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description='Scan BassDrive.com every few hours.')
    parser.add_argument('hours', metavar='N', type=int, nargs='+',
                        help='The number of hours between each scan')
    args = parser.parse_args()
    logging.info( "Scanning every {} hours.".format( args.hours[0] ) )
    gProcessVars['hours'] = args.hours[0]

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
    logging.info('Scrape active and waiting...')

    #sched.add_job( startWebScraping, 'interval', minutes=5 )

    while True:
        okToScrape = datetime.now() >= datetime.fromisoformat(
            gProcessVars['db']['last_scan']) + timedelta(hours=gProcessVars['hours'])
    
        if DEBUG == True or okToScrape == True:
            startWebScraping(ROOTURL)




