#!/usr/bin/env python

import os
import os.path
import sqlalchemy as sa

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Config
import db


db.Base.metadata.bind = sa.create_engine(os.environ['DATABASE_URL'])
db.Base.metadata.drop_all()
db.Base.metadata.create_all()



