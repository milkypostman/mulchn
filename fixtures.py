from fixture import SQLAlchemyFixture, DataSet
from datetime import datetime
from db import Account, Twitter

fixture = SQLAlchemyFixture(env={'AccountData': Account, 'TwitterData': Twitter})

class AccountData(DataSet):
    class admin:
        created = datetime.now()
        username = u"admin"
        admin = True
        active = True
        image_url = u"..."

    class normal:
        created = datetime.now()
        username = u"normal"
        admin = False
        active = True
        image_url = u"..."


class TwitterData(DataSet):
    class admin:
        screen_name = u"admin"
        account = AccountData.admin

    class normal:
        screen_name = u"normal"
        account = AccountData.normal





