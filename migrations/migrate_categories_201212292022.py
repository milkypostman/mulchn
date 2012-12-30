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

    for question in db.questions.find():
        print("Processing {0}...".format(question['question']))
        if 'category' not in question:
            print "No category..."
            continue

        question['tags'] = [question['category']]
        del question['category']
        db.questions.save(question)




if __name__ == '__main__':
    main()


