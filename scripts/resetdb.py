#!/usr/bin/env python

import os.path
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from flask import Config

import db
import os

config = Config("")
config.from_envvar('MULCHN_CONFIG')

database_url = os.environ.get("DATABASE_URL", config['DATABASE_URL'])
engine = create_engine(database_url, echo=True)

with engine.begin() as conn:
    db.Twitter.metadata.drop_all(conn)
    db.Twitter.metadata.create_all(conn)
    db.Account.metadata.drop_all(conn)
    db.Account.metadata.create_all(conn)
