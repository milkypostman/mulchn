import os
import mulchn
import unittest
from pymongo import Connection
import tempfile

class MulchnTestCase(unittest.TestCase):

    def setUp(self):
        mulchn.app.config['MONGODB_URL'] = "mongodb://localhost/mulchn-test"
        mulchn.app.config['TESTING'] = True
        self.app = mulchn.app.test_client()

    def test_empty_db(self):
        rv = self.app.get('/')
        print rv

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
