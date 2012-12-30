#!/usr/bin/env python

from pymongo import Connection
from urlparse import urlsplit
import os


def main():
    """
    """

    mongo_url = os.environ['MONGODB_URL']
    mongo_db = urlsplit(mongo_url).path[1:]
    db = Connection(mongo_url, tz_aware=True)[mongo_db]

    for user in db.users.find():
        print("Processing {0}...".format(user['username']))
        newtwitter = {}
        newtwitter['id'] = int(user['twitter']['user_id'])
        user['twitter'] = newtwitter
        db.users.save(user)




if __name__ == '__main__':
    main()


