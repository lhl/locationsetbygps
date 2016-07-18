#!/usr/bin/python3


import foursquare
import json
import logging
import pymysql
import os
from   pprint import pprint
import sys
import time
import traceback


# VARS
SLEEP = 600 # Once every 10 min is fine

# Max: https://developer.foursquare.com/docs/users/checkins
LIMIT = 250


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
  global LIMIT

  logging.info('STARTING new check...')

  # 4SQ  (if you need a new token run the bin/4sq-auth.py)
  creds = json.load(open('%s/4sq.creds' % PRIVATE))
  client = foursquare.Foursquare(access_token=creds['token'])

  # DB
  dbc = json.load(open('%s/db.creds' % PRIVATE))
  conn = pymysql.connect(user=dbc['user'], passwd=dbc['passwd'], db=dbc['db'], charset='utf8')

  # Get Checkins
  sql = 'SELECT MAX(time) AS t FROM location'
  cursor = conn.cursor(pymysql.cursors.DictCursor)
  cursor.execute(sql)
  r = cursor.fetchone()
  AFTER = r['t']
  AFTER -= 10
  if AFTER < 0:
    AFTER = 0
  cursor.close()

  try:
    params = {'limit': LIMIT, 'sort': 'oldestfirst', 'afterTimestamp': AFTER}
    checkins = client.users.checkins(params=params)
  except:
    logging.info('4SQ API ERROR') 
    e = sys.exc_info()[0]
    if e.__name__ == 'ValueConstraintError':
      # will always throw <class 'pyasn1.type.error.ValueConstraintError'>
      pass
    else:
      return

  sql = """INSERT INTO location
           (service, uid, type, time, tzoffset, lat, lon, city, state, country, cc, venue, json)
           VALUES
           (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
  # for checkin in client.users.all_checkins():
  for checkin in checkins['checkins']['items']:

    try: 
      # bad data
      if 'venue' not in checkin:
        checkin['venue'] = {'location': {}}
      if 'state'  not in checkin['venue']['location']:
        checkin['venue']['location']['state'] = None
      if 'city'  not in checkin['venue']['location']:
        checkin['venue']['location']['city'] = None
      if 'country'  not in checkin['venue']['location']:
        checkin['venue']['location']['country'] = None
      if 'cc'  not in checkin['venue']['location']:
        checkin['venue']['location']['cc'] = None
      if 'lat'  not in checkin['venue']['location']:
        checkin['venue']['location']['lat'] = None
      if 'lng'  not in checkin['venue']['location']:
        checkin['venue']['location']['lng'] = None

      data = ('foursquare', checkin['id'], checkin['type'], checkin['createdAt'], checkin['timeZoneOffset'], checkin['venue']['location']['lat'], checkin['venue']['location']['lng'], checkin['venue']['location']['city'], checkin['venue']['location']['state'], checkin['venue']['location']['country'], checkin['venue']['location']['cc'], json.dumps(checkin['venue']), json.dumps(checkin))

      cursor = conn.cursor(pymysql.cursors.DictCursor)
      cursor.execute(sql, data)
      conn.commit()
      logging.info('ADDED %s: %s' % (checkin['createdAt'], checkin['venue']['name']))
      cursor.close()
    except pymysql.IntegrityError:
      logging.info('DUPE skipping %s: %s' % (checkin['createdAt'], checkin['venue']['name']))
    pass

  logging.info('DONE')

if __name__ == '__main__':
  while 1:
    main()
    logging.info('SLEEPING for %ss' % SLEEP)
    time.sleep(SLEEP)
