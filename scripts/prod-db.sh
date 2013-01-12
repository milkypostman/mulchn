#!/bin/bash

heroku config -a mulchn | sed -n "s/DATABASE_URL: *\(.*\)$/\1/p"
