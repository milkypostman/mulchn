from hashlib import sha1
from pymongo import Connection
import json
import mulchn
import os
import tempfile
import unittest

class MulchnTestCase(unittest.TestCase):
    def setUp(self):
        mulchn.app.config['MONGODB_URL'] = "mongodb://localhost/mulchn-test"
        mulchn.app.config['TESTING'] = True
        mulchn.app.config['CSRF_ENABLED'] = False
        self.app = mulchn.app.test_client()
        self.db = Connection()['mulchn-test']


class MulchnEmptyTestCase(MulchnTestCase):
    @classmethod
    def setUpClass(cls):
        connection = Connection()
        connection.drop_database("mulchn-test")

    def test_empty_db(self):
        resp = self.app.get('/v1/questions/')
        data = json.loads(resp.data)
        assert data == []


    def test_redirect(self):
        resp = self.app.post('/question/add/', data={})
        assert resp.status_code == 302
        assert "Redirecting..." in resp.data
        assert "/login/twitter" in resp.data



class MulchnUserTestCase(MulchnTestCase):
    """Tests that require at least a user."""
    @classmethod
    def setUpClass(cls):
        connection = Connection()
        connection.drop_database("mulchn-test")
        user = json.load(open("fixtures/user_milkypostman.json"))
        cls._id = connection["mulchn-test"].users.insert(user)


    def test_add_page(self):
        with self.app.session_transaction() as session:
            session['user_id'] = self._id
        resp = self.app.get('/question/add/')
        assert resp.status_code == 200
        assert 'form' in resp.data


    def test_add_error(self):
        with self.app.session_transaction() as sess:
            sess['user_id'] = self._id
        resp = self.app.post('/question/add/', data={
            "tags":"tag1, tag2",
            "question":"Question 1",
            "answers-1":"Question 1 Answer 1",
            })
        assert resp.status_code == 200
        assert "field is required" in resp.data

    def test_add_success(self):
        with self.app.session_transaction() as sess:
            sess['user_id'] = self._id
        resp = self.app.post('/question/add/', data={
            "tags":"tag1, tag2",
            "question":"Question 1",
            "answers-1":"Question 1 Answer 1",
            "answers-2":"Question 1 Answer 2",
            })
        # after successfully adding we should get a redirect
        assert resp.status_code == 302

        questions = list(self.db.questions.find())
        assert len(questions) == 1

        question = questions[0]

        assert question['owner'] == self._id
        assert question['question'] == "Question 1"
        assert question['tags'] == ['tag1', 'tag2']

        answers = question['answers']

        assert answers[0]['answer'] == "Question 1 Answer 1"
        assert answers[1]['answer'] == "Question 1 Answer 2"
        assert '_id' in answers[0]
        assert '_id' in answers[1]

    def test_no_user(self):
        resp = self.app.get("/")
        assert "login" in resp.data
        assert ">login<" in resp.data
        assert "/login/twitter/" in resp.data


    def test_user_logged_in(self):
        with self.app.session_transaction() as sess:
            sess['user_id'] = self._id

        resp = self.app.get("/")

        assert "milkypostman" in resp.data
        assert ">logout<" in resp.data
        assert "/logout/" in resp.data


    def test_vote(self):
        pass

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
