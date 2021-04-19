import os
import json
from datetime import datetime, timedelta
import logging
import argparse
from apscheduler.schedulers.blocking import BlockingScheduler

from workers.webscraper import ScraperThread


ROOTURL = 'http://archives.bassdrivearchive.com/'
DBFILE = 'filedata.json'
DEBUG = False
MIN_MINUTES_THRESHOLD = 5

gProcessVars = {
    'scrape_thread': None,
    'db': None,
    'wait_minutes': MIN_MINUTES_THRESHOLD
}

  
# Function to handle the scraping thread
def startWebScraping():
    logging.info("Starting web scraping from {}...".format(ROOTURL))
    gProcessVars['scrape_thread'] = ScraperThread(
        ROOTURL, onScraperUpdate, onScraperComplete)
    gProcessVars['scrape_thread'].start()
    gProcessVars['scrape_thread'].join()

# Doesn't do anything for now.   
def onScraperUpdate( obj ):
    pass

# Closes the task and stores the results
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

# Writes out the collected records as a json object
def writeDb( self ):
    gProcessVars['db']['output'] = ''
    with open( DBFILE, "w") as f:
        json.dump( self.db, f, indent=4)        


# Main entry point
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description='Scan BassDrive.com every few minutes.')
    parser.add_argument('minutes', metavar='N', type=int, nargs='+',
                        help='The number of minutes between each scan')
    args = parser.parse_args()
    logging.info( "Scanning every {} minutes.".format( args.minutes[0] ) )
    gProcessVars['wait_minutes'] = args.minutes[0]

    # We can't go less than a few minutes
    if gProcessVars['wait_minutes'] < MIN_MINUTES_THRESHOLD:
        logging.warning("Setting wait minutes to minimum of {} minutes.".format(
            MIN_MINUTES_THRESHOLD))
        gProcessVars['wait_minutes'] = MIN_MINUTES_THRESHOLD

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

    # Start the scheduler immediately
    sched = BlockingScheduler()
    sched.add_job(startWebScraping, 'interval',
                  minutes=gProcessVars['wait_minutes'])
    sched.start()

    



