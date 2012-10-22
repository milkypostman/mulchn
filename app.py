#!/usr/bin/env python

from bson.objectid import ObjectId, InvalidId
from datetime import datetime
from flask import Flask
from flask import Response
from flask import abort
from flask import flash
from flask import g
from flask import json
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask.ext import wtf
from flaskext.coffee import coffee
from itertools import izip_longest
from pymongo import Connection
from urlparse import urlsplit
from wtforms.validators import StopValidation

import oauth2 as oauth
import os
import time
import urllib
import urlparse
import twitter


"""
db.questions.remove({added : {$gt: ISODate("2012-10-15T20:18:20.138Z")}})
"""

class TagListField(wtf.Field):
    widget = wtf.TextInput()

    def _value(self):
        return u', '.join(self.data) if self.data else ''

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = [x.strip() for x in valuelist[0].split(',')]
        else:
            self.data = []


class AddForm(wtf.Form):
    tags = TagListField("Tags (comma separated: music, beatles, ...)", validators=[wtf.InputRequired()])
    question = wtf.StringField("Question", validators=[wtf.DataRequired()])
    answers = wtf.FieldList(wtf.TextField("Answer", validators=[wtf.DataRequired()]), min_entries=2, max_entries=5)


def json_handler(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, ObjectId):
        return unicode(obj)
    raise TypeError, \
        'Object of type {0} with value {0} is not JSON serializable'.format(
            type(obj), repr(objc))

def jsonify(*args, **kwargs):
    return app.response_class(json.dumps(dict(*args, **kwargs),
                                         default=json_handler,
                                         indent=None if request.is_xhr else 2),
                              mimetype="application/json")

def tags():
    return sorted(c['name'] for c in g.db.tags.find())


def render(template, **kwargs):
    # kwargs['tags'] = tags()
    return render_template(template, **kwargs)



app = Flask(__name__)
app.config.from_object('config')
app.config.from_envvar('MULCHN_SETTINGS', silent=True)

if app.debug:
    coffee(app)

@app.before_request
def init_mongodb():
    mongo_url = os.environ.get('MONGOHQ_URL', app.config['MONGODB_URL'])
    mongo_db = urlsplit(mongo_url).path[1:]
    g.db = Connection(mongo_url, tz_aware=True)[mongo_db]


@app.teardown_request
def close_mongodb(exception):
    del g.db

@app.before_request
def find_user():
    if 'user_id' in session and not 'user' in session:
        user =  g.db.users.find_one({'_id':session['user_id']})
        if user is None:
            session.pop('user_id')
        else:
            g.user = user


@app.context_processor
def inject_user():
    try:
        return dict(user = g.user)
    except AttributeError:
        return dict()


def errors_dict(fields):
    errors = {}
    for field in fields:
        if field.type == "CSRFTokenField": continue

        if field.type == "FieldList":
            errors.update(errors_dict(field))
        elif field.errors:
            errors[field.id] = field.errors

    return errors


@app.errorhandler(401)
def invalid_login():
    return jsonify({'errors': [{'message':"Access denied."}]}), 401

@app.route("/question/<question>/", methods=['GET'])
def question(question):
    try:
        obj = g.db.questions.find_one({"_id":ObjectId(question)})
    except InvalidId:
        obj = None

    if obj is None:
        abort(404)

    return str(obj)



@app.route("/question/add/", methods=['GET', 'PUT', 'POST'])
def question_add():
    if not hasattr(g, 'user'):
        session['after_login'] = 'question_add'
        return redirect(url_for('login_twitter'))

    if request.method in ["PUT", "POST"]:
        formdata = request.form.copy()
        formdata.update(request.files)

        # cleanup answer fields if people were sloppy
        # FIXME: will not work with double digits
        answer_fields = sorted(f for f in formdata.iteritems() if f[0].startswith("answers"))
        answer_keys = [f[0] for f in answer_fields]
        answer_vals = [f[1] for f in answer_fields if f[1] != ""]
        answer_fields = izip_longest(answer_keys, answer_vals)

        # relabel answers
        for key, val in answer_fields:
            if val is not None:
                formdata[key] = val
            else:
                del formdata[key]

        form = AddForm(formdata)

        if form.validate_on_submit():
            question = dict(question=form['question'].data, author=g.user['_id'])
            question['answers'] = [{'_id': ObjectId(), 'answer':ans} for ans in form['answers'].data]
            question['added'] = datetime.utcnow()

            g.db.questions.insert(question)

            flash("Added Question: {0}".format(question['question']))
            return redirect(url_for('questions'))
    else:
        form = AddForm()
    return render("add.html", form=form)


def clean_old_votes(question):
    qid = ObjectId(question)
    uid = ObjectId(g.user['_id'])
    q = g.db.questions.find_one({'_id':qid}, {'answers':1})
    if q is None:
        abort(404)
    for ans in q['answers']:
        g.db.questions.update({'_id':qid, 'answers._id':ans['_id']},
                              {"$pull" : {"answers.$.votes": {"user":uid}}})

@app.route("/v1/question/vote/", methods=['GET', 'POST','PUT'])
def v1_vote():
    if not hasattr(g, 'user'):
        return invalid_login()

    data = request.form
    votedata = {'user': g.user['_id']}
    votedata.update({key:data[key] for key in
                     ['latitude',
                      'longitude',
                      'accuracy',
                      'speed',
                      'geotimestamp',
                  ] if key in data})



    clean_old_votes(data['question'])
    qid = ObjectId(data['question'])
    g.db.questions.update({'_id':qid, 'answers._id':ObjectId(data['answer'])},
                          {'$addToSet': {'answers.$.votes': votedata}})

    question = g.db.questions.find_one({"_id": qid})
    ret = {}
    ret['question'] = question
    ret['vote'] = data['answer']

    return jsonify(ret)


def user_answers():
    return {unicode(q['_id']):user_answer(q['answers']) for q in
            g.db.questions.find({"answers.votes.user": g.user['_id']},
                                {"answers.$._id": "1"})}

def user_answer(answers):
    if len(answers) > 1:
        app.logger.error("Answers ({0}) has multiple votes for {1}!".format(
            ', '.join(a['_id'] for a in answers), uid))

    return answers[0]['_id']


@app.route("/v1/questions/")
def v1_questions():

    votes = {}
    if hasattr(g, 'user'):
        votes = user_answers()

    questions = list(g.db.questions.find().sort('added', -1))

    return jsonify({'questions':questions, 'votes':votes})


@app.route("/<tag>/")
def tag(tag):
    questions = g.db.questions.find({'tags':tag})
    questions = list(questions)
    return render("questions.html",
                           questions=questions,
                           tag=tag)

@app.route("/login/")
def login():
    return redirect(url_for('login_twitter'))

@app.route("/login/twitter/")
def login_twitter():
    consumer = oauth.Consumer(app.config['TWITTER_CONSUMER_KEY'],
                              app.config['TWITTER_CONSUMER_SECRET'])
    client = oauth.Client(consumer)

    callback = '{0}{1}'.format(app.config['SITE_URL'], url_for('login_twitter_authenticated'))
    resp, content = client.request(app.config['TWITTER_REQUEST_TOKEN_URL'],
                                   "POST",
                                   body=urllib.urlencode({'oauth_callback':callback}))
    if resp['status'] != '200':
        abort(404)

    request_token = dict(urlparse.parse_qsl(content))
    session['twitter_request_token_secret'] = request_token['oauth_token_secret']



    return redirect("{0}?oauth_token={1}".format(app.config["TWITTER_AUTHENTICATE_URL"],
                                        request_token['oauth_token']))

@app.route("/login/twitter/authenticated/")
def login_twitter_authenticated():
    token = oauth.Token(request.args['oauth_token'],
                        session['twitter_request_token_secret'])

    token.set_verifier(request.args['oauth_verifier'])


    consumer = oauth.Consumer(app.config['TWITTER_CONSUMER_KEY'],
                              app.config['TWITTER_CONSUMER_SECRET'])
    client = oauth.Client(consumer, token)

    resp, content = client.request(app.config['TWITTER_ACCESS_TOKEN_URL'],
                                   "POST")

    if resp['status'] != '200':
        return redirect(url_for("login_twitter"))

    data = dict(urlparse.parse_qsl(content))

    try:
        user = g.db.users.find_one({'twitter.user_id': data['user_id']})
        session['user_id'] = user["_id"]
    except TypeError:
        user = {'username': data['screen_name'], 'twitter': data}
        session['user_id'] = g.db.users.insert(user)


    flash("Logged in as {0}.".format(user['username']))

    if 'after_login' in session:
        return redirect(url_for(session.pop('after_login')))

    return redirect(url_for("questions"))



@app.route("/logout/")
def logout():
    if session.pop('user_id', None) is not None and hasattr(g, 'user'):
        flash("{0} has been logged out.".format(g.user['username']))
    return redirect(url_for("questions"))



@app.route("/register/twitter/")
def register_twitter():
    if not 'twitter_access_token' in session:
        return redirect(url_for("login_twitter"))

    access_token = session['twitter_access_token']

    api = twitter.Api(consumer_key=app.config['TWITTER_CONSUMER_KEY'],
                      consumer_secret=app.config['TWITTER_CONSUMER_SECRET'],
                      access_token_key = access_token['oauth_token'],
                      access_token_secret = access_token['oauth_token_secret'])
    try:
        return str(api.VerifyCredentials())
    except twitter.TwitterError:
        session.pop('twitter_access_token')
        return redirect(url_for("login_twitter"))




@app.route("/")
def questions():
    return render("questions.html")




if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)
