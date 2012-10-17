#!/usr/bin/env python

from bson.objectid import ObjectId, InvalidId
from datetime import datetime
from flask import Flask
from flask import Response
from flask import abort, flash, redirect, url_for
from flask import g
from flask import jsonify
from flask import render_template
from flask import request
from flask.ext import wtf
from itertools import izip_longest
from pymongo import Connection
from urlparse import urlsplit
from wtforms.validators import StopValidation

import os

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
    tags = TagListField("Tags (comma separated: music, beatles, ...)", validators=[wtf.Required()])
    question = wtf.TextField("Question", validators=[wtf.Required()])
    answers = wtf.FieldList(wtf.TextField("Answer", validators=[wtf.Required()]), min_entries=2, max_entries=5)


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


@app.route("/")
def root():
    questions = g.db.questions.find().sort('added', -1)
    questions = list(questions)
    return render("questions.html",
                           questions=questions)




if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)
