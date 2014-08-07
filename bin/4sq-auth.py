#!/usr/bin/python

import foursquare
import json

CRED_FILE = '/www/locationsetbygps/private/4sq.creds'

# Load credentials - This pulls 
creds = json.load(open(CRED_FILE))
print creds

print 'ID     : %s' % creds['id']
print 'SECRET : %s' % creds['secret']
print 'TOKEN  : %s' % creds['token']

print
print "Let's get a new token..."
print

# Construct the client object
client = foursquare.Foursquare(client_id=creds['id'], client_secret=creds['secret'], redirect_uri='http://locationsetbygps.com/oauth/print.php')

# Build the authorization url for your app
auth_uri = client.oauth.auth_url()

print "Copy and paste this into your browser:"
print auth_uri
print

# Get Code
code = raw_input("Once you've auth'd, copy and paste the code here: ")
code = code.strip()

# Get Token
token = client.oauth.get_token(code)

# Write it down
creds['token'] = token
json.dump(creds, open(CRED_FILE, 'w'))
print "private/4sq.creds updated!"
