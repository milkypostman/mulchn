#!/usr/bin/env python

import os.path
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from urlparse import urlsplit
import db
import pymongo
from mulchn import jsonify

mongo_url = os.environ['MONGOHQ_URL']
mongo_db = urlsplit(mongo_url).path[1:]
mdb = pymongo.Connection(mongo_url, tz_aware=True)[mongo_db]

# mdb = pymongo.Connection()['mulchn']
db.engine.echo = True

alook = {}
me = None
for user in mdb.users.find():
    a = db.Account()
    a.username = user['username']

    t = db.Twitter()
    t.screen_name = a.username
    t.id = user['twitter']['id']

    a.twitter = t
    alook[user['_id']] = a
    if a.username == 'milkypostman':
        me = a

    db.session.add(a)
    db.session.add(t)


for mq in mdb.questions.find():
    q = db.Question()
    q.text = mq['question']
    q.tag_list = mq.get('tags', [])
    q.owner = alook.get(mq['owner'], me)
    q.added = mq['added']
    for ma in mq['answers']:
        a = db.Answer()
        a.question = q
        a.text = ma['answer']
        for mv in ma['votes']:
            if mv['user'] not in alook: continue
            v = db.Vote()
            v.account = alook[mv['user']]
            v.answer = a
            if 'latitude' in mv and 'longitude' in mv:
                v.latitude = mv['latitude']
                v.longitude = mv['longitude']
            elif 'position' in mv:
                v.latitude = mv['position']['coords']['latitude']
                v.longitude = mv['position']['coords']['longitude']
                v.raw = jsonify(mv['position'])
            db.session.add(v)
        db.session.add(a)
    db.session.add(q)


db.session.commit()









