#!/usr/bin/env python



from db import *

a = Account()
a.username = "dummy"
session.add(a)

q = Question()
q.text = "Question 1?"
q.tag_list = ['tag1', 'tag2', 'tag3']
q.answer_list = ['q1a1', 'q1a2', 'q1a3']
q.account = a

session.add(q)
session.commit()
