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
from itertools import izip_longest
from pymongo import Connection
from urlparse import urlsplit
from wtforms.validators import StopValidation

import oauth2 as oauth
import os, os.path
import subprocess
import time
import urllib
import urlparse
import twitter
import warnings

app = Flask(__name__)
app.config.from_object('config')
app.config.from_envvar('MULCHN_SETTINGS', silent=True)



class TagListField(wtf.Field):
    """ parse a tag list field """
    widget = wtf.TextInput()

    def _value(self):
        return u', '.join(self.data) if self.data else ''

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = [x.strip() for x in valuelist[0].split(',')]
        else:
            self.data = []


class AddForm(wtf.Form):
    """Add Question Form"""
    tags = TagListField("Tags (comma separated: music, beatles, ...)", validators=[wtf.InputRequired()])
    question = wtf.StringField("Question", validators=[wtf.DataRequired()])
    answers = wtf.FieldList(wtf.TextField("Answer", validators=[wtf.DataRequired()]), min_entries=2, max_entries=5)


@app.context_processor
def inject_user():
    try:
        return dict(user = g.user)
    except AttributeError:
        return dict()


def json_handler(obj):
    """
    special JSON handler

    special handling of `obj` for the following types:
    - datetime
    - Objectid

    """

    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, ObjectId):
        return unicode(obj)
    raise TypeError, \
        'Object of type {0} with value {0} is not JSON serializable'.format(
            type(obj), repr(objc))


def jsonify(data):
    """
    jsonfiy `data`
    """
    return app.response_class(json.dumps(data,
                                         default=json_handler,
                                         indent=None if request.is_xhr else 2),
                              mimetype="application/json")


def render(template, **kwargs):
    """
    Customizable render function.
    """
    return render_template(template, **kwargs)



@app.before_request
def init_mongodb():
    """
    Initialize MongoDB instance into global application context.

    Uses either `MONGOHQ_URL` variable from environment or configuration file.
    """

    mongo_url = os.environ.get('MONGOHQ_URL', app.config['MONGODB_URL'])
    mongo_db = urlsplit(mongo_url).path[1:]

    with warnings.catch_warnings():
        warnings.simplefilter('ignore', UserWarning)
        g.db = Connection(mongo_url, tz_aware=True)[mongo_db]


@app.teardown_request
def close_mongodb(exception):
    """
    Close up MongoDB instance.
    """
    pass
    # del g.db


@app.before_request
def find_user():
    """
    Load user information into the global app context if exists in the database.
    """
    if 'user_id' not in session: return

    user = g.db.users.find_one({'_id':session['user_id']})
    if user is None:
        session.pop('user_id')
        return

    g.user = user



def errors_dict(fields):
    """
    Generate dictionary of errors for a set of form fields.
    Supports FieldList subforms.

    Dictionary format is (field.id, field.errors).

    CSRFTokenField type fields are ignored.
    """

    errors = {}
    for field in fields:
        if field.type == "CSRFTokenField": continue

        if field.type == "FieldList":
            errors.update(errors_dict(field))
        elif field.errors:
            errors[field.id] = field.errors

    return errors


@app.errorhandler(401)
def access_denied(errors = []):
    """
    Generate a 401 JSON response for key 'errors' from kwargs.

    Defaults to [{"message": "Access Denied."}]
    """

    if not errors:
        errors = [{'message': "Access Denied."}]

    return jsonify({'errors': errors}), 401


@app.route("/question/<_id>/", methods=['GET'])
def question(_id):
    """
    Fetch question with specified `_id`.

    Arguments:
    - `_id`: QuestionId to return data on.
    """

    try:
        obj = g.db.questions.find_one({"_id":ObjectId(question)})
    except InvalidId:
        obj = None

    if obj is None:
        abort(404)

    return str(obj)


@app.route("/question/add/", methods=['GET', 'PUT', 'POST'])
def question_add():
    """
    Add a question to the database.

    GET - Display the Add form.
    POST - Verify form data and insert question into the database or
           render form with errors.
    PUT - Alias for POST
    """

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
            question = dict(question=form['question'].data, owner=g.user['_id'])
            question['answers'] = [{'_id': ObjectId(), 'answer':ans} for ans in form['answers'].data]
            question['added'] = datetime.utcnow()
            question['tags'] = form['tags'].data

            g.db.questions.insert(question)

            flash("Added Question: {0}".format(question['question']))
            return redirect(url_for('questions'))
    else:
        form = AddForm()
    return render("add.html", form=form)



def clean_old_votes(questionId):
    """
    Clean up extra votes on the question `questionId` for the current user.

    Arguments:
    - `questionId`: QuestionId to clean up.
    """
    uid = ObjectId(g.user['_id'])
    q = g.db.questions.find_one({'_id':questionId}, {'answers':1})
    if q is None:
        abort(404)
    for ans in q['answers']:
        g.db.questions.update({'_id':questionId, 'answers._id':ans['_id']},
                              {"$pull" : {"answers.$.votes": {"user":uid}}})

@app.route("/v1/question/vote/", methods=['POST','PUT'])
def v1_vote():
    """
    Vote on a question.

    Requires a POST or PUT with JSON dictionary containing:
    - `_id`: ObjectId of the question to vote on.
    - `vote`: ObjectId of answer to vote for.
    """

    if not hasattr(g, 'user'):
        return access_denied()

    data = request.json
    votedata = {'user': g.user['_id']}
    if data.get('position'):
        votedata['position'] = data['position']

    qid = ObjectId(data['_id'])
    clean_old_votes(qid)
    vote = ObjectId(data['vote'])

    g.db.questions.update({'_id':qid, 'answers._id':vote},
                          {'$addToSet': {'answers.$.votes': votedata}})

    ret = question_dict(g.db.questions.find_one({"_id": qid}),
                        {qid:vote})
    ret['vote'] = vote

    return jsonify(ret)


@app.route("/v1/question/<question>", methods=['DELETE'])
def v1_question(question):
    """
    CRUD method for single question.

    **Currently only supports the DELETE option.**
    """

    if not hasattr(g, 'user'):
        return access_denied()

    if request.method == 'DELETE':
        try:
            obj = g.db.questions.find_one({"_id":ObjectId(question)})
        except InvalidId:
            abort(404)

        if obj['owner'] == g.user['_id']:
            g.db.questions.remove({"_id": obj['_id']})
        else:
            access_denied()
    else:
        abort(404)

    return jsonify({'response': 'OK'})


def user_answers():
    return {q['_id']:user_answer(q['answers']) for q in
            g.db.questions.find({"answers.votes.user": g.user['_id']},
                                {"answers.$._id": "1"})}

def user_answer(answers):
    if len(answers) > 1:
        app.logger.error("Answers ({0}) has multiple votes for {1}!".format(
            ', '.join(a['_id'] for a in answers), uid))

    return answers[0]['_id']


ANSWER_KEYS = ['answer', '_id']

def answer_dict(answer):
    ret = {key:answer[key] for key in ANSWER_KEYS if key in answer}
    if hasattr(g, 'user'):
        ret['votes'] = len(answer.get('votes', []))

    return ret



QUESTION_KEYS = ['question', '_id', 'added', 'owner']

def question_dict(question, votes):
    ret = {key:question[key] for key in QUESTION_KEYS}
    ret['answers'] = [answer_dict(ans) for ans in question['answers']]

    if question["_id"] in votes:
        ret['vote'] = votes[question["_id"]]

    return ret


@app.route("/v1/questions/")
def v1_questions():
    votes = {}
    if hasattr(g, 'user'):
        votes = user_answers()

    questions = [question_dict(q, votes) for q in g.db.questions.find().sort('added', -1)]

    return jsonify(questions)


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
    # initialize untokenized client
    consumer = oauth.Consumer(app.config['TWITTER_CONSUMER_KEY'],
                              app.config['TWITTER_CONSUMER_SECRET'])
    client = oauth.Client(consumer)

    # build callback URL
    callback = '{0}{1}'.format(app.config['SITE_URL'], url_for('login_twitter_authenticated'))

    # request a temporary request token
    resp, content = client.request(app.config['TWITTER_REQUEST_TOKEN_URL'],
                                   "POST",
                                   body=urllib.urlencode({'oauth_callback':callback}))
    if resp['status'] != '200':
        abort(404)


    # get temporary oauth secret token
    request_token = dict(urlparse.parse_qsl(content))
    session['twitter_request_token_secret'] = request_token['oauth_token_secret']



    # redirect to Twitter login page
    return redirect("{0}?oauth_token={1}".format(app.config["TWITTER_AUTHENTICATE_URL"],
                                        request_token['oauth_token']))

@app.route("/login/twitter/authenticated/")
def login_twitter_authenticated():

    # build token from oauth token redirected to us
    # goes with the secret token we recieved in `login_twitter()`
    token = oauth.Token(request.args['oauth_token'],
                        session['twitter_request_token_secret'])

    token.set_verifier(request.args['oauth_verifier'])


    # request an access token
    consumer = oauth.Consumer(app.config['TWITTER_CONSUMER_KEY'],
                              app.config['TWITTER_CONSUMER_SECRET'])
    client = oauth.Client(consumer, token)

    resp, content = client.request(app.config['TWITTER_ACCESS_TOKEN_URL'],
                                   "POST")

    if resp['status'] != '200':
        flash("Failed to login!")
        return redirect(url_for("questions"))


    # data contains our final token and secret for the user
    data = dict(urlparse.parse_qsl(content))

    # either create or update user information
    try:
        user = g.db.users.find_one({'twitter.user_id': data['user_id']})
        session['user_id'] = user["_id"]
        user['twitter'] ['oauth_token']= data['oauth_token']
        user['twitter'] ['oauth_token_secret']= data['oauth_token_secret']
        g.db.users.save(user)
    except TypeError:
        user = {'username': data['screen_name'], 'twitter': data}
        session['user_id'] = g.db.users.insert(user)


    # try to add friends
    if 'friends' not in user['twitter']:
        print "getting friends"
        api = twitter.Api(consumer_key=app.config['TWITTER_CONSUMER_KEY'],
                          consumer_secret=app.config['TWITTER_CONSUMER_SECRET'],
                          access_token_key = user['twitter']['oauth_token'],
                          access_token_secret = user['twitter']['oauth_token_secret'])

        try:
            user['twitter']['friends'] = [f.AsDict() for f in api.GetFriends()]
            g.db.users.save(user)
        except twitter.TwitterError:
            pass


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



def coffeescript_paths():
    static_dir = app.root_path + app.static_url_path
    return [os.path.join(path, fn)
            for path, _, filenames in os.walk(static_dir)
            for fn in filenames
            if os.path.splitext(fn)[1] == '.coffee']


def compile_coffeescript():
    static_url_path = app.static_url_path
    static_dir = app.root_path + app.static_url_path

    cs_paths = coffeescript_paths()

    for cs_path in cs_paths:
        js_path = os.path.splitext(cs_path)[0] + '.js'
        js_mtime = os.path.getmtime(js_path) if os.path.isfile(js_path) else -1

        cs_mtime = os.path.getmtime(cs_path)
        if cs_mtime > js_mtime:
            print("Compiling {0}".format(cs_path))
            subprocess.call(['coffee', '-c', cs_path], shell=False)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    if app.debug:
        compile_coffeescript()
    app.run(host="0.0.0.0", port=port, extra_files=coffeescript_paths())



