#!/usr/bin/env python

from pymongo import Connection

def main():
    """
    """

    mongo_url = os.environ['MONGODB_URL']
    mongo_db = urlsplit(mongo_url).path[1:]
    db = Connection(mongo_url, tz_aware=True)[mongo_db]





if __name__ == '__main__':
    main()


