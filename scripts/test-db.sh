#!/bin/bash

heroku config -a mulchn-test | sed -n "s/DATABASE_URL: *\(.*\)$/\1/p"
