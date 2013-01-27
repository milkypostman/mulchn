from hashlib import sha1
from pymongo import Connection
import json
import mulchn
import os
import fixtures
import tempfile
import unittest
import db

class MulchnTestCase(unittest.TestCase):
    def setUp(self):
        mulchn.app.config['TESTING'] = True
        mulchn.app.config['CSRF_ENABLED'] = False
        self.app = mulchn.app.test_client()
        db.configure_engine("postgres://localhost/mulchn-test")

    @classmethod
    def setUpClass(cls):
        print "MulchnTestCase"
        db.configure_engine("postgres://localhost/mulchn-test")
        db.Base.metadata.drop_all(bind=db.engine)
        db.Base.metadata.create_all(bind=db.engine)




class MulchnEmptyTestCase(MulchnTestCase):
    def test_redirect(self):
        resp = self.app.post('/add', data={})
        assert resp.status_code == 302
        assert "Redirecting..." in resp.data
        assert "/login" in resp.data

    def test_no_user(self):
        resp = self.app.get("/")
        assert "/login" in resp.data


    def test_empty_db(self):
        resp = self.app.get('/', headers=[('X-Requested-With', 'XMLHttpRequest')])
        data = json.loads(resp.data)
        assert data['questions'] == []
        assert data['nextPage'] == None
        assert data['prevPage'] == None
        assert data['numPages'] == 0



class MulchnUserTestCase(MulchnTestCase):
    """Tests that require at least a user."""
    @classmethod
    def setUpClass(cls):
        super(MulchnUserTestCase, cls).setUpClass()

        print "MulchnUserTestCase"
        fixture = fixtures.fixture
        fixture.engine = db.engine
        data = fixture.data(fixtures.AccountData, fixtures.TwitterData)
        data.setup()

        cls.normal_account = db.Account.query.filter_by(username='normal').one()
        cls.admin_account = db.Account.query.filter_by(username='admin').one()
        cls.normal_id = db.Account.query.filter_by(username='normal').one().id
        cls.admin_id = db.Account.query.filter_by(username='admin').one().id


    def test_nil(self):
        pass

    def test_add_page(self):
        with self.app.session_transaction() as session:
            session['account_id'] = self.normal_id

        resp = self.app.get('/add')
        assert resp.status_code == 200
        assert 'form' in resp.data


    def test_add_error(self):
        with self.app.session_transaction() as session:
            session['account_id'] = self.normal_id

        resp = self.app.post('/add', data={
            "tags":"tag1, tag2",
            "question":"Question 1",
            "answers-1":"Question 1 Answer 1",
            })
        assert resp.status_code == 200
        assert "field is required" in resp.data

    def test_add_success(self):
        with self.app.session_transaction() as session:
            session['account_id'] = self.normal_id

        resp = self.app.post('/add', data={
            "tags":"tag1, tag2",
            "question":"Question 1",
            "answers-1":"Question 1 Answer 1",
            "answers-2":"Question 1 Answer 2",
            })

        # after successfully adding we should get a redirect
        assert resp.status_code == 302

        questions = list(db.Question.query.all())
        assert len(questions) == 1

        question = questions[0]

        assert question.owner.id == self.normal_id
        assert question.text == "Question 1"
        assert question.tag_list == ['tag1', 'tag2']

        answers = question.answers

        assert answers[0].text == "Question 1 Answer 1"
        assert answers[1].text == "Question 1 Answer 2"


    def test_user_logged_in(self):
        with self.app.session_transaction() as sess:
            sess['account_id'] = self.normal_id

        resp = self.app.get("/")

        assert "normal" in resp.data
        assert "/logout" in resp.data


#     def test_vote(self):
#         pass

#     def tearDown(self):
        # pass
class MulchnManyTestCase(MulchnUserTestCase):
    """Tests that require at least a user."""
    @classmethod
    def setUpClass(cls):
        super(MulchnManyTestCase, cls).setUpClass()

        print "MulchnManyTestCase"

        # FIXME: add a bunch of randomly generated questions here





if __name__ == '__main__':
    unittest.main()
