#!/usr/bin/python


import foursquare
import json
import logging
import MySQLdb
import os
from   pprint import pprint
import sys
import time


# VARS
SLEEP = 600 # Once every 10 min is fine


### PATHS
HOME = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../')
PRIVATE = '%s/private' % HOME


### LOGGING
logging.basicConfig(level=logging.INFO,
                    format = '%(asctime)s : %(levelname)-8s : %(message)s',
                    # datefmt = '%Y-%m-%d %H:%M:%S',
                    filename='%s/logs/4sq-sync.log' % HOME
)
if sys.stdout.isatty():
  debug = 1
  console = logging.StreamHandler()
  console.setLevel(logging.DEBUG)
  formatter = logging.Formatter('%(asctime)s : %(levelname)-8s : %(message)s')
  console.setFormatter(formatter)

  logging.getLogger('').addHandler(console)
else:
  debug = 0


### The Loop
def main():
  logging.info('STARTING new check...')

  # 4SQ  (if you need a new token run the bin/4sq-auth.py)
  creds = json.load(open('%s/4sq.creds' % PRIVATE))
  client = foursquare.Foursquare(access_token=creds['token'])

  # DB
  dbc = json.load(open('%s/db.creds' % PRIVATE))
  conn = MySQLdb.connect(user=dbc['user'], passwd=dbc['passwd'], db=dbc['db'], charset='utf8')

  # Get Checkins
  '''
  TODO use vs time... https://developer.foursquare.com/docs/users/checkins
  auto increment offsets until ok...
  '''
  checkins = client.users.checkins(params={'limit': 10}) 

  sql = """INSERT INTO location
           (service, uid, type, time, tzoffset, lat, lon, city, state, country, cc, venue, json)
           VALUES
           (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
  # for checkin in client.users.all_checkins():
  for checkin in checkins['checkins']['items']:
    try: 
      # bad data
      if not checkin.has_key('venue'):
        checkin['venue'] = {'location': {}}
      if not checkin['venue']['location'].has_key('state'):
        checkin['venue']['location']['state'] = None
      if not checkin['venue']['location'].has_key('city'):
        checkin['venue']['location']['city'] = None
      if not checkin['venue']['location'].has_key('country'):
        checkin['venue']['location']['country'] = None
      if not checkin['venue']['location'].has_key('cc'):
        checkin['venue']['location']['cc'] = None
      if not checkin['venue']['location'].has_key('lat'):
        checkin['venue']['location']['lat'] = None
      if not checkin['venue']['location'].has_key('lng'):
        checkin['venue']['location']['lng'] = None

      data = ('foursquare', checkin['id'], checkin['type'], checkin['createdAt'], checkin['timeZoneOffset'], checkin['venue']['location']['lat'], checkin['venue']['location']['lng'], checkin['venue']['location']['city'], checkin['venue']['location']['state'], checkin['venue']['location']['country'], checkin['venue']['location']['cc'], json.dumps(checkin['venue']), json.dumps(checkin))

      cursor = conn.cursor(MySQLdb.cursors.DictCursor)
      cursor.execute(sql, data)
      conn.commit()
      logging.info('ADDED %s: %s' % (checkin['createdAt'], checkin['venue']['name']))
      cursor.close()
    except MySQLdb.IntegrityError, e:
      logging.info('DUPE skipping %s: %s' % (checkin['createdAt'], checkin['venue']['name']))
    pass

  print 'DONE'

if __name__ == '__main__':
  while 1:
    main()
    print 'SLEEPING for %ss' % SLEEP
    time.sleep(SLEEP)
