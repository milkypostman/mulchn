#!/usr/bin/env python

from bson.objectid import ObjectId, InvalidId
from datetime import datetime
from flask import Flask
from flask import Response
from flask import abort
from flask import flash
from flask import g
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask.ext import wtf
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


def tags():
    return sorted(c['name'] for c in g.db.tags.find())


def render(template, **kwargs):
    # kwargs['tags'] = tags()
    return render_template(template, **kwargs)



app = Flask(__name__)
app.config.from_object('config')
app.config.from_envvar('MULCHN_SETTINGS', silent=True)


@app.before_request
def before_request():
    mongo_url = os.environ.get('MONGOHQ_URL', app.config['MONGODB_URL'])
    mongo_db = urlsplit(mongo_url).path[1:]
    g.db = Connection(mongo_url)[mongo_db]


@app.teardown_request
def after_request(exception):
    del g.db


def errors_dict(fields):
    errors = {}
    for field in fields:
        if field.type == "CSRFTokenField": continue

        if field.type == "FieldList":
            errors.update(errors_dict(field))
        elif field.errors:
            errors[field.id] = field.errors

    return errors


@app.route("/question/add/", methods=['GET', 'PUT', 'POST'])
def question_add():

    if request.method in ["PUT", "POST"]:
        formdata = request.form.copy()
        formdata.update(request.files)

        answer_fields = sorted(f for f in formdata.iteritems() if f[0].startswith("answers"))
        answer_keys = [f[0] for f in answer_fields]
        answer_vals = [f[1] for f in answer_fields if f[1] != ""]

        answer_fields = izip_longest(answer_keys, answer_vals)

        for key, val in answer_fields:
            if val is not None:
                formdata[key] = val
            else:
                del formdata[key]

        form = AddForm(formdata)

        if form.validate_on_submit():
            question = {field.name:field.data for field in form if field.type != "CSRFTokenField"}
            question['added'] = datetime.now()
            g.db.questions.insert(question)
            flash("Added Question: {0}".format(question['question']))
            return redirect(url_for('root'))
        elif request.is_xhr:
            d = errors_dict(form)
            resp = jsonify(d)
            resp.status_code = 404
            return resp
    else:
        form = AddForm()
    return render("add.html", form=form)


@app.route("/question/<question>/", methods=['GET'])
def question(question):
    try:
        obj = g.db.questions.find_one({"_id":ObjectId(question)})
    except InvalidId:
        obj = None

    if obj is None:
        abort(404)

    return str(obj)


@app.route("/add/", methods=["POST", "GET"])
def add():
    form = AddForm()
    if request.method == "POST" and form.validate():
        question = {field.name:field.data for field in form
                               if field.type != "CSRFTokenField"}
        question['added'] = datetime.now()
        resp = g.db.questions.insert(question)
        flash("Question submitted.")
        return redirect(url_for('tag', tag=form.tag.data))



@app.route("/<tag>/")
def tag(tag):
    questions = g.db.questions.find({'tags':tag})
    questions = list(questions)
    return render("questions.html",
                           questions=questions,
                           tag=tag)



@app.route("/login/twitter/")
def login_twitter():
    if 'twitter_access_token' in session:
        return redirect(url_for("register_twitter"))

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
    access_token = dict(urlparse.parse_qsl(content))
    session['twitter_access_token'] = access_token

    if resp['status'] != '200':
        return redirect(url_for("login_twitter"))


    return redirect(url_for("register_twitter"))



@app.route("/register/twitter/")
def register_twitter():
    print session
    if not 'twitter_access_token' in session:
        return redirect(url_for("login_twitter"))

    access_token = session['twitter_access_token']

    api = twitter.Api(consumer_key=app.config['TWITTER_CONSUMER_KEY'],
                      consumer_secret=app.config['TWITTER_CONSUMER_SECRET'],
                      access_token_key = access_token['oauth_token'],
                      access_token_secret = access_token['oauth_token_secret'])
    return str(api.VerifyCredentials())



@app.route("/")
def root():
    questions = g.db.questions.find().sort('added', -1)
    questions = list(questions)
    return render("questions.html",
                           questions=questions)




if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)
