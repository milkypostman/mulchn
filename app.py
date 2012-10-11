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


@app.route("/s/<section>/")
def view_section(section):
    questions = g.db["questions.{0}".format(section)].find()
    questions = list(questions)
    return render_template("section.html",
                           questions=questions,
                           section=section)


@app.route("/")
def root():
    sections = [c[10:] for c in g.db.collection_names()
                if c.startswith("questions.")]
    return render_template("index.html", sections=sections)

if __name__ == '__main__':
    app.run()
