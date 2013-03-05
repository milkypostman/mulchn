## config.py --- Mulchn Configuration

import os

SECRET_KEY=os.environ.get('SECRET_KEY', '')

DATABASE_URL="postgres://localhost/mulchn"

CSRF_ENABLED = True

TWITTER_REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
TWITTER_AUTHORIZE_URL = 'https://api.twitter.com/oauth/authorize'
TWITTER_AUTHENTICATE_URL = 'https://api.twitter.com/oauth/authenticate'
TWITTER_ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
TWITTER_CONSUMER_KEY = os.environ.get('TWITTER_CONSUMER_KEY', '')
TWITTER_CONSUMER_SECRET = os.environ.get('TWITTER_CONSUMER_SECRET', '')

PAGINATION_NUM = 256
