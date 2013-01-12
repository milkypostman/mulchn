#!/bin/bash

TESTING_DB=`heroku config -a mulchn-test | sed -n "s/DATABASE_URL: *\(.*\)$/\1/p"`
PRODUCTION_DB=`heroku config -a mulchn | sed -n "s/DATABASE_URL: *\(.*\)$/\1/p"`

echo "$TESTING_DB -> $PRODUCTION_DB"

pg_dump -c -O $PRODUCTION_DB | psql $TESTING_DB
