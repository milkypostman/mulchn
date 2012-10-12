#!/usr/bin/env python

from pymongo import Connection

from flask import Flask
from flask import g
from flask import render_template
app = Flask(__name__)
app.config.from_object('config')
app.config.from_envvar('QQ_SETTINGS', silent=True)

@app.before_request
def before_request():
    g.db = Connection()[app.config['DATABASE']]

@app.teardown_request
def after_request(exception):
    del g.db


def categories():
    return sorted(c['name'] for c in g.db.categories.find())


def render(template, **kwargs):
    kwargs['categories'] = categories()
    return render_template(template, **kwargs)

@app.route("/add/", {"POST", "GET"})
def add():
    return render("add.html")



@app.route("/<category>/")
def view_category(category):
    questions = g.db["{0}".format(category)].find()
    questions = list(questions)
    return render("category.html",
                           questions=questions,
                           category=category)


@app.route("/")
def root():
    return render("index.html")

if __name__ == '__main__':
    app.run()
