#!/usr/bin/env python

from datetime import datetime
from db import Account, Twitter, Vote, VoteHistory, Tag, Question, Answer, AccountFollow
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
from log import create_logger
from flask.ext.assets import Environment, Bundle
from functools import wraps
from itertools import izip_longest
from urlparse import urlsplit

import db
import flask
import logging
import math
import oauth2 as oauth
import os
import os.path
import sqlalchemy as sa
import subprocess
import time
import twitter
import urllib
import urlparse
import warnings

log = create_logger("mulchn")


def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    app.config.from_envvar('MULCHN_CONFIG', silent=True)
    app.config['ASSETS_UGLIFYJS_EXTRA_ARGS'] = '-m'
    app.config.setdefault('PAGINATION_NUM', 5)

    # db.configure_engine(os.environ.get("DATABASE_URL", app.config.get('DATABASE_URL')))

    assets = Environment(app)
    css_slicklist = Bundle('css/slicklist.less',
                           filters="less",
                           output="css/slicklist.css")
    assets.register('css_slicklist', css_slicklist)

    css_main = Bundle('css/main.less',
                      filters="less",
                      output="css/main.css")
    assets.register('css_main', css_main)

    js_app = Bundle('js/add.coffee',
                    'js/dialog.coffee',
                    'js/geolocation.coffee',
                    'js/logindialog.coffee',
                    'js/router.coffee',
                    'js/account.coffee',
                    'js/question/model.coffee',
                    'js/question/collection.coffee',
                    'js/question/view.coffee',
                    'js/question/list.coffee',
                    'js/question/paginator.coffee',
                    'js/main.coffee',
                    filters='coffeescript,rjsmin',
                    output='js/m.js')
    assets.register('js_app', js_app)

    js_frameworks = Bundle(
        'js/lib/jquery.js',
        'js/lib/lodash.js',
        'js/lib/backbone.js',
        'js/lib/bootstrap.js',
        'js/lib/geolocation.js',
        filters='rjsmin',
        output='js/frameworks.js')
    assets.register('js_frameworks', js_frameworks)

    js_d3 = Bundle(
        'js/lib/topojson.js',
        'js/lib/d3.js',
        # filters='rjsmin',
        output='js/d3.topojson.js')
    assets.register('js_d3', js_d3)

    return app

app = create_app()


### Forms

def TagLength(max=32, message=None):
    if message is None:
        message = "Tag cannot exceed %i characters." % (max)

    def tag_length(form, field):
        if any(len(val) > max for val in field.data):
            raise wtf.ValidationError(message)

    return tag_length


class TagListField(wtf.Field):
    """ parse a tag list field """
    widget = wtf.TextInput()

    def _value(self):
        return u', '.join(self.data) if self.data else ''

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = list({x.strip() for x in valuelist[0].lower().split(',')})
            self.data = [d for d in self.data if d]
        else:
            self.data = []

strip_filter = lambda s: s.strip() if s else None


class AddForm(wtf.Form):
    """Add Question Form"""
    tags = TagListField("Tags (comma separated: music, beatles, ...)",
                        validators=[wtf.InputRequired(), TagLength(max=32)])

    question = wtf.StringField("Question",
                               validators=[wtf.DataRequired(),
                                           wtf.Length(max=128)],
                               filters=[strip_filter])
    answers = wtf.FieldList(wtf.TextField("Answer",
                                          validators=[wtf.DataRequired(),
                                                      wtf.Length(max=128)],
                                          filters=[strip_filter]),
                            min_entries=2,
                            max_entries=5)


### Request Setup
@app.before_request
def remove_trailing_slash():
    if request.path != '/' and request.path.endswith('/'):
        return redirect(request.path[:-1])


@app.context_processor
def inject_static_url():
    static_url = app.static_url_path
    if not static_url.endswith('/'):
        static_url += '/'
    return dict(STATIC_URL=static_url)


@app.context_processor
def inject_account():
    try:
        return dict(account=g.account)
    except AttributeError:
        return dict()


@app.teardown_request
def close_sqlalchemy(exception):
    log.debug("commit or rollback")
    commit()
    db.session.remove()


@app.before_request
def start_timer():
    g.starttime = time.time()


@app.after_request
def report_load_time(response):
    if hasattr(g, 'starttime'):
        log.info("load time: %s", time.time() - g.starttime)
    return response


@app.before_request
def find_account():
    """
    Load account information into the global app context if exists in the database.
    """
    if 'account_id' not in session:
        return

    account = Account.query.filter_by(id=session['account_id']).first()
    if account is None:
        session.pop('account_id')
    else:
        g.account = account


### Response Functions
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

    raise TypeError(
        'Object of type {0} with value {0} is not JSON serializable'.format(
        type(obj), repr(obj)))


def jsonify(data, indent=None):
    """
    jsonfiy `data`
    """
    return json.dumps(data, default=json_handler, indent=indent)


def render_json(data):
    indent = None if request.is_xhr else 2

    return app.response_class(jsonify(data, indent=indent),
                              mimetype="application/json")


def render_taglist(template, **kwargs):
    if 'taglist' not in kwargs:
        kwargs['taglist'] = [(tag.name, count) \
                               for tag, count in tag_rank_query()]

    return render_template(template, **kwargs)


def render(template, **kwargs):
    """
    Customizable render function.
    """
    return render_template(template, **kwargs)


#### Error Handlers
def page_not_found(errors=[]):
    if not errors:
        errors = [{'message': "Page not found."}]

    return render_json({'errors': errors}), 401


def access_denied(errors=[]):
    """
    Generate a 401 JSON response for key 'errors' from kwargs.

    Defaults to [{"message": "Access Denied."}]
    """

    if not errors:
        errors = [{'message': "Access Denied."}]

    return render_json({'errors': errors}), 401


### Helper Functions
def errors_dict(fields):
    """
    Generate dictionary of errors for a set of form fields.
    Supports FieldList subforms.

    Dictionary format is (field.id, field.errors).

    CSRFTokenField type fields are ignored.
    """

    errors = {}
    for field in fields:
        if field.type == "CSRFTokenField":
            continue

        if field.type == "FieldList":
            errors.update(errors_dict(field))
        elif field.errors:
            errors[field.id] = field.errors

    return errors


def clean_old_votes(questionId):
    """Clean up extra votes on the question `questionId` for the
    current account.

    The current user is assumed to be the vote. Has to be.

    :param questionId: QuestionId to clean up.

    :return: True if there are old votes, False otherwise.
    """

    old_vote = Vote.query.join(Answer).filter(
        Vote.account_id == g.account.id,
        Answer.question_id == questionId).first()

    if old_vote is not None:
        log.info("remove old vote: answer.id=%s, question.id=%s, account.id=%s",
                 old_vote.answer_id, questionId, g.account.id)
        db.session.add(old_vote.create_history())
        db.session.delete(old_vote)
        return True
    return False


def question_vote_locations(question):
    """Creates the geojson necessary for rendering.

    :param question: question to generate this data for.
    """

    locations = []

    # just make up a counter
    identifier = 0
    for answer in question.answers:
        log.debug("populate vote locations: answer.id=%s", answer.id)
        for v in answer.votes:
            locations.append(
                dict(type="Feature",
                     id=identifier,
                     geometry=dict(type="Point",
                                   coordinates=[v.longitude, v.latitude],
                                   properties=dict(answer=answer.id))))
        identifier += 1

    return locations


ANSWER_KEYS = ['text', 'id']


def answer_dict(answer, vote):
    ret = {key: getattr(answer, key) for key in ANSWER_KEYS}

    if hasattr(g, 'account'):
        ret['votes'] = len(answer.votes)
        log.debug("followee votes lookup")
        followers = {f.id: f.username for f in g.account.following}

        ret['followees'] = [{'id': v.answer_id,
                             'username': followers[v.account_id]}
                             for v in answer.votes
                             if v.account_id in followers]
        ret['followee_votes'] = len(ret['followees'])

    return ret


QUESTION_KEYS = ['text', 'id', 'added']


def question_dict(question, votes):
    """
    Arguments:
    - `question`: question data
    - `votes`: dictionary mapping question._id to answer._id for all
    questions the account has made.
    """
    if question is None:
        return None

    ret = {key: getattr(question, key) for key in QUESTION_KEYS}
    ret['tags'] = question.tag_list.copy()

    if question.id in votes:
        ret['vote'] = votes[question.id]
        ret['geo'] = question_vote_locations(question)

    if hasattr(g, 'account') and question.owner == g.account:
        ret['owner'] = g.account.id

    ret['tags'] = sorted([t.name for t in question.tags])

    ret['answers'] = [answer_dict(ans, ret.get('vote')) for ans in question.answers]
    return ret


def question_id_dict(question_id):
    votes = {}
    if hasattr(g, 'account'):
        log.debug("account votes lookup")
        votes = {v.answer.question_id: v.answer.id for v in g.account.votes}

    q = Question.query.filter_by(active=True, id=question_id).first()

    return question_dict(q, votes)


def questions_dict(questions):
    # logged in account gets their votes
    votes = {}
    if hasattr(g, 'account'):
        log.debug("account votes lookup")
        ## FIXME: when a limited subset, only look at those questions
        votes = {v.answer.question_id: v.answer.id for v in g.account.votes}

    return [question_dict(q, votes) for q in questions]


def tag_rank_query():
    '''return list of tags and corresponding number of questions

    :return: list of tuples of (tag, count)
    '''
    tags = Tag.query.add_column(sa.func.count(Question.id).label('count')) \
        .join(Tag.questions).group_by(Tag.id).order_by('count desc')

    return tags


### Decorators
def login_required(f):
    """ decorator to check for valid login

    automatically redirects back to the current function after login
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        if not hasattr(g, 'account'):
            if request.is_xhr:
                return access_denied()
            session['url_after_login'] = url_for(f.__name__)
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return wrapper


### API Functions
@app.route("/vote", methods=['POST', 'PUT'])
@login_required
def vote():
    """
    Vote on a question.

    Requires a POST or PUT with JSON dictionary containing:
    - `_id`: ObjectId of the question to vote on.
    - `vote`: ObjectId of answer to vote for.
    """

    data = request.json
    log.debug("vote data: %s", data)

    question_id = data['id']

    log.info("answer lookup: id=%s, question.id=%s", data['vote'], question_id)
    answer = Answer.query.filter(Answer.question_id == question_id,
                                 Answer.id == data['vote']).first()

    if answer is None:
        abort(404)

    log.debug("clean old votes")
    if not clean_old_votes(question_id):
        answer.question.modified = datetime.now()

    log.info("new vote: user=%s, question=%s, answer=%s",
             g.account.id, question_id, answer.id)
    vote = Vote(account=g.account, answer=answer)
    pos = data.get('position')
    if pos is not None:
        vote.position_raw = jsonify(pos)
        if 'coords' in pos:
            vote.latitude = pos['coords']['latitude']
            vote.longitude = pos['coords']['longitude']

    db.session.add(vote)
    db.session.commit()

    log.debug("populate return data")
    ret = question_dict(Question.query.filter(Question.id == question_id).first(),
                        {question_id: vote.answer_id})

    log.info("commit vote record(s)")
    commit()

    log.debug("returning vote info: %s", ret)
    return render_json(ret)


### Login / Logout
@app.route("/login")
def login():
    if hasattr(g, 'account'):
        return redirect(url_for("questions"))
    return render("login.html")


@app.route("/logout")
def logout():
    if session.pop('account_id', None) is not None and hasattr(g, 'account'):
        flash("{0} has been logged out.".format(g.account.username), 'warn')
    return redirect(request.referrer)
    return redirect(url_for("questions"))


### Pages
@app.route("/new", defaults={'page': 1})
@app.route("/new/<int:page>")
def new(page):
    log.debug("new questions page: %d", page)

    if page < 1:
        abort(404)

    questions = Question.query.filter_by(active=True, private=False) \
        .order_by(sa.sql.expression.desc(Question.added))

    c = questions.count()

    pagination = app.config['PAGINATION_NUM']

    limit = pagination
    offset = (page - 1) * pagination
    q = questions.limit(limit).offset(offset)

    pages = int(math.ceil(c / float(pagination)))

    payload = {'questions': questions_dict(q),
               'nextPage': page + 1 if page < pages else None,
               'prevPage': page - 1 if page > 1 else None,
               'numPages': pages}

    if request.is_xhr:
        return render_json(payload)

    return render_taglist("questions.html", data=jsonify(payload))


@app.route("/u/<string:username>/unanswered", defaults={'page': 1})
@app.route("/u/<string:username>/unanswered/<int:page>")
def user_unanswered(username, page):
    log.debug("%s unanswered page: %d", username, page)

    if page < 1:
        abort(404)

    answered = db.session.query(Question.id) \
        .join(Answer, Vote, Account) \
        .filter(Account.username == username)

    if not answered:
        abort(404)

    questions = Question.query.filter_by(active=True, private=False) \
        .filter(sa.func.not_(Question.id.in_(answered))) \
        .order_by(sa.sql.expression.desc(Question.modified))

    c = questions.count()

    pagination = app.config['PAGINATION_NUM']

    limit = pagination
    offset = (page - 1) * pagination
    q = questions.limit(limit).offset(offset)

    pages = int(math.ceil(c / float(pagination)))

    payload = {'questions': questions_dict(q),
               'nextPage': page + 1 if page < pages else None,
               'prevPage': page - 1 if page > 1 else None,
               'numPages': pages}

    if request.is_xhr:
        return render_json(payload)

    return render_taglist("questions.html", data=jsonify(payload))


@app.route("/", defaults={'page': 1})
@app.route("/<int:page>")
def questions(page):
    log.debug("questions page: %d", page)

    if page < 1:
        abort(404)

    questions = Question.query.filter_by(active=True, private=False) \
        .order_by(sa.sql.expression.desc(Question.modified))

    c = questions.count()
    pagination = app.config['PAGINATION_NUM']

    limit = pagination
    offset = (page - 1) * pagination
    q = questions.limit(limit).offset(offset)

    pages = int(math.ceil(c / float(pagination)))

    payload = {'questions': questions_dict(q),
               'nextPage': page + 1 if page < pages else None,
               'prevPage': page - 1 if page > 1 else None,
               'numPages': pages}

    if request.is_xhr:
        return render_json(payload)

    return render_taglist("questions.html",
                  data=jsonify(payload))


@app.route("/t", defaults={'tag_name': None, 'page': 1})
@app.route("/t/<tag_name>", defaults={'page': 1})
@app.route("/t/<tag_name>/<int:page>")
def tag(tag_name, page):
    if tag_name is None:
        return render("tags.html",
                      navname="tags",
                      taglist=[(tag.name, count)
                               for tag, count in tag_rank_query()])

    questions = Question.query.join((Question.tags, Tag)) \
        .filter(Tag.name == tag_name,
                Question.active == True,
                Question.private == False) \
                .order_by(sa.sql.expression.desc(Question.added))

    pagination = app.config['PAGINATION_NUM']

    c = questions.count()
    limit = pagination
    offset = (page - 1) * pagination
    q = questions.limit(limit).offset(offset)

    if not q:
        abort(404)

    pages = int(math.ceil(c / float(pagination)))

    payload = {'questions': questions_dict(q),
               'nextPage': page + 1 if page < pages else None,
               'prevPage': page - 1 if page > 1 else None,
               'numPages': pages}

    if request.is_xhr:
        return render_json(payload)

    return render_taglist("questions.html",
                  data=jsonify(payload))


@app.route("/add", methods=['GET', 'PUT', 'POST'])
@login_required
def question_add():
    """
    Add a question to the database.

    GET - Display the Add form.
    POST - Verify form data and insert question into the database or
    render form with errors.
    PUT - Alias for POST
    """

    if request.method in ["PUT", "POST"]:
        formdata = request.form.copy()
        formdata.update(request.files)

        # cleanup_answer fields if people were sloppy
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
            question = Question()
            question.owner = g.account
            question.text = form['question'].data
            question.tag_list = form['tags'].data
            question.answer_list = form['answers'].data
            question.modified = datetime.now()
            db.session.add(question)

            flash("Added Question: {0}".format(question.text), 'success')
            return redirect(url_for('question', question_id=question.id))
    else:
        form = AddForm()
    return render("add.html", form=form)


@app.route("/q/<question_id>", methods=['GET', 'DELETE'])
def question(question_id):
    """
    Fetch question with specified `question_id`.

    Arguments:
    - `question_id`: QuestionId to return data on.
    """
    if request.method == 'DELETE':
        log.info("question lookup: id=%s", question_id)
        question = Question.query.filter_by(id=question_id).first()
        if not question:
            abort(404)
        elif question.owner_id == g.account.id or g.account.admin:
            log.info("removing question %s", question.id)
            question.active = False
            question.removed = datetime.now()
            db.session.add(question)
            return render_json({'response': 'OK'})
        else:
            return access_denied()

    q = question_id_dict(question_id)
    if q is None:
        abort(404)

    return render_taglist("questions.html", data=jsonify(q))


### Twitter MumboJumbo
@app.route("/login/twitter")
def login_twitter():
    if 'next' in request.args:
        session['url_after_login'] = request.args['next']
    else:
        session['url_after_login'] = request.referrer

    # initialize untokenized client
    consumer = oauth.Consumer(app.config['TWITTER_CONSUMER_KEY'],
                              app.config['TWITTER_CONSUMER_SECRET'])
    client = oauth.Client(consumer)

    # build callback URL
    callback = '{0}{1}'.format(request.host_url, url_for('login_twitter_authenticated'))

    # request a temporary request token
    resp, content = client.request(app.config['TWITTER_REQUEST_TOKEN_URL'],
                                   "POST",
                                   body=urllib.urlencode({'oauth_callback': callback}))
    if resp['status'] != '200':
        abort(404)

    # get temporary oauth secret token
    request_token = dict(urlparse.parse_qsl(content))
    session['twitter_request_token_secret'] = request_token['oauth_token_secret']


    # redirect to Twitter login page
    return redirect("{0}?oauth_token={1}".format(app.config["TWITTER_AUTHENTICATE_URL"],
                                                 request_token['oauth_token']))


def commit():
    """
    Commit the current database session and automatically rollback if
    an error occurs.

    Return:
    True on success
    False on error
    """

    try:
        db.session.commit()
    except sa.exc.InvalidRequestError:
        db.session.rollback()
        return False

    return True


@app.route("/login/twitter/authenticated")
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
        flash("Failed to login!", 'error')
        return redirect(url_for("questions"))

    # data contains our final token and secret for the account
    data = dict(urlparse.parse_qsl(content))

    oauth_token = data['oauth_token']
    oauth_token_secret = data['oauth_token_secret']

    api = twitter.Api(consumer_key=app.config['TWITTER_CONSUMER_KEY'],
                      consumer_secret=app.config['TWITTER_CONSUMER_SECRET'],
                      access_token_key=oauth_token,
                      access_token_secret=oauth_token_secret)

    try:
        twitter_data = api.VerifyCredentials().AsDict()
    except twitter.TwitterError:
        flash("Cannot validate Twitter credentials.", 'error')
        return redirect(url_for("questions"))

    # print twitter_data

    # either create or update account information
    twaccount = Twitter.query.filter_by(id=twitter_data['id']).first()

    if twaccount is None:
        account = Account()
        db.session.add(account)

        twaccount = Twitter()
        twaccount.id = twitter_data['id']
        twaccount.account = account
    else:
        account = twaccount.account

    twaccount.screen_name = account.username = twitter_data['screen_name']
    account.image_url = twitter_data['profile_image_url']
    twaccount.raw = jsonify(twitter_data)

    twaccount.oauth_token = oauth_token
    twaccount.oauth_token_secret = oauth_token_secret
    db.session.add(twaccount)

    # try to add friends
    try:
        friendIDs = []
        cursor = -1
        while True:
            data = api.GetFriendIDs(cursor=cursor)
            friendIDs += data['ids']
            if 'next_cursor' not in data or \
                    data['next_cursor'] == 0 or \
                    data['next_cursor'] == data['previous_cursor']:
                break

            cursor = data['next_cursor']

        twaccount.follows = [db.TwitterFollow(follower_id=account.id, followee_id=f) for f in friendIDs]
        account.following = [f.account for f in twaccount.following]
        log.debug("following: %s", [a.username for a in account.following])

    except twitter.TwitterError:
        pass

    log.info("commiting twitter login info: account.id=%s", account.id)
    if not commit():
        flash("Error while logging in.", 'error')
        return redirect(url_for("questions"))

    session['account_id'] = twaccount.account_id

    flash("Logged in as {0}.".format(account.username), 'success')
    if 'url_after_login' in session:
        return redirect(session.pop('url_after_login'))

    return redirect(url_for("questions"))


@app.route("/test/twitter")
@login_required
def test_twitter():
    access_token = g.account['twitter']

    api = twitter.Api(consumer_key=app.config['TWITTER_CONSUMER_KEY'],
                      consumer_secret=app.config['TWITTER_CONSUMER_SECRET'],
                      access_token_key=access_token['oauth_token'],
                      access_token_secret=access_token['oauth_token_secret'])
    try:
        return render(u"raw.html",
                      title=u"Twitter Data",
                      content=u"<ul>" + "".join(
                u"<li>{0}</li>".format(u.name) for u in api.GetFriends()
                ) + u"</ul>")
    except twitter.TwitterError:
        return str("TwitterError")


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    extra_files = []
    if app.debug:
        db.engine.echo = True
        log.setLevel(logging.DEBUG)
        extra_files.append('dev_config.py')

    log.info("starting up...")
    app.run(host="0.0.0.0", port=port, extra_files=extra_files)
