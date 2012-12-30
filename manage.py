#!/usr/bin/env python

from mulchn import app, assets
from flask.ext.script import Manager
from flask.ext.assets import ManageAssets

# configure your app
manager = Manager(app)
manager.add_command("assets", ManageAssets(assets))

if __name__ == "__main__":
    manager.run()

