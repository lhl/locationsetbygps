#!/bin/bash

# Using wp-cli
/bin/date
cd /www/locationsetbygps/wp
/usr/local/bin/wp core update
/usr/local/bin/wp plugin update --all
/usr/local/bin/wp theme update --all
