#!/usr/bin/env python


from flask import Flask
from flask import g
from flask import request
from flask import abort
from flask import jsonify
from flask import render_template
from flask import Response
from flask.ext.wtf import Form, TextField, Required, FieldList
from wtforms.validators import StopValidation
from pymongo import Connection

import os


class AddForm(Form):
    category = TextField("Category", validators=[Required()])
    question = TextField("Question", validators=[Required()])
    answers = FieldList(TextField("Answer", validators=[Required()]), min_entries=2, max_entries=5)



def categories():
    return sorted(c['name'] for c in g.db.categories.find())


def render(template, **kwargs):
    kwargs['categories'] = categories()
    return render_template(template, **kwargs)



app = Flask(__name__)
app.config.from_object('config')
app.config.from_envvar('QQ_SETTINGS', silent=True)


@app.before_request
def before_request():
    g.db = Connection()[app.config['DATABASE']]


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

@app.route("/question/", methods=['PUT'])
@app.route("/question/<question>/", methods=['GET'])
def question(question=None):
    if request.method == "PUT":
        form = AddForm()
        if form.validate_on_submit():
            g.db.questions.insert({field.name:field.data for field in form})
            return Response()
        else:
            d = errors_dict(form)
            resp = jsonify(d)
            resp.status_code = 404
            return resp
    return "GET"


@app.route("/add/")
def add():
    form = AddForm()
    return render("add.html", form=form)


@app.route("/<category>/")
def category(category):
    questions = g.db.questions.find({'category':category})
    questions = list(questions)
    return render("category.html",
                           questions=questions,
                           category=category)


@app.route("/")
def root():
    return render("index.html")




if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)
