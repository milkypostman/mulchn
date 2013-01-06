from sqlalchemy import Column, Boolean, BigInteger, DateTime, ForeignKey, Integer, Numeric, String, Table, Text
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship, backref, deferred
from sqlalchemy.ext.associationproxy import association_proxy

import sqlalchemy as sa
import flask
import os
import re

config = flask.Config("")
config.from_envvar('MULCHN_CONFIG')

database_url = os.environ.get("DATABASE_URL", config['DATABASE_URL'])
engine = sa.create_engine(database_url)
session = sa.orm.scoped_session(sa.orm.sessionmaker(bind=engine))

class _Base(object):
    @declared_attr
    def __tablename__(cls):
        """
        Convert CamelCase class name to underscores_between_words
        table name.
        """

        name = cls.__name__
        return (
            name[0].lower() +
            re.sub(r'([A-Z])', lambda m:"_" + m.group(0).lower(), name[1:])
        )


Base = declarative_base(cls=_Base)
Base.query = session.query_property()


class AccountFollow(Base):
    follower_id = Column(ForeignKey('account.id'), primary_key=True)
    followee_id = Column(ForeignKey('account.id'), primary_key=True)


class Account(Base):
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=sa.sql.func.now())
    username = Column(String(128))
    active = Column(Boolean, default=True)
    admin = Column(Boolean, default=False)
    following = relationship("Account",
                             secondary='account_follow',
                             primaryjoin=AccountFollow.follower_id==id,
                             secondaryjoin=AccountFollow.followee_id==id,
                             backref="followers"
                             )

    voted_answers = association_proxy('votes', 'answer',
                                      creator=lambda answer: Vote(account=None, answer=answer))

    def __init__(self, username=None):
        """

        Arguments:
        - `self`:
        - `username`:
        """
        if username is not None: self.username = username


class TwitterFollow(Base):
    follower_id = Column(ForeignKey('twitter.id'), primary_key=True)
    followee_id = Column(BigInteger, index=True, primary_key=True)

    def __init__(self, follower_id=None, followee_id=None):
        """

        Arguments:
        - `follower_id`:
        - `followee_id`:
        """
        if follower_id is not None: self.follower_id = follower_id
        if followee_id is not None: self.followee_id = followee_id


def _twitter_follow_find_or_create(followee_id):
    follow = TwitterFollow.query.filter(TwitterFollow.followee_id==followee_id).first()
    if not(follow):
        follow = TwitterFollow()
        follow.followee_id = followee_id
        # if aufoflush=False used in the session, then uncomment below
        #session.add(tag)
        #session.flush()
    return follow


class Twitter(Base):
    id = Column(BigInteger, primary_key=True)
    screen_name = Column(String(128))
    oauth_token = Column(String(128))
    oauth_token_secret = Column(String(128))

    account_id = Column(ForeignKey('account.id'))
    account = relationship("Account", uselist=False, lazy="joined",
                           backref=backref("twitter", uselist=False))

    raw = deferred(Column(Text))

    follows = relationship("TwitterFollow",
                                primaryjoin="TwitterFollow.follower_id==Twitter.id",
                                cascade="all, delete-orphan")

    follow_id_list = association_proxy('follows', 'followee_id',
                                          creator=_twitter_follow_find_or_create)

    following = relationship("Twitter",
                             secondary="twitter_follow",
                             primaryjoin="TwitterFollow.follower_id==Twitter.id",
                             secondaryjoin="TwitterFollow.followee_id==Twitter.id",
                             backref="followers",
                             )

class VoteHistory(Base):
    id = Column(Integer, primary_key=True)
    account_id = Column(ForeignKey('account.id'))
    answer_id = Column(ForeignKey('answer.id'))
    timestamp = Column(DateTime(), default=sa.sql.func.now())
    account = relationship("Account")#, backref="vote_history")
    answer = relationship("Answer")#, backref="vote_history")

    position_raw = deferred(Column(Text))

    def __init__(self, account=None, answer=None):
        """

        Arguments:
        - `self`:
        - `account`:
        - `answer`:
        """
        if account is not None: self.account = account
        if answer is not None: self.answer = answer




class Vote(Base):
    account_id = Column(ForeignKey('account.id'), primary_key=True)
    answer_id = Column(ForeignKey('answer.id'), primary_key=True)
    timestamp = Column(DateTime, default=sa.sql.func.now())
    account = relationship("Account", backref="votes")
    answer = relationship("Answer", lazy="joined", backref=backref("votes", lazy="joined"))
    position_raw = deferred(Column(Text))

    latitude = Column(Numeric())
    longitude = Column(Numeric())


    def __init__(self, account=None, answer=None):
        """
        Arguments:
        - `self`:
        - `account`:
        - `answer`:
        """
        if account is not None: self.account = account
        if answer is not None: self.answer = answer

    def create_history(self):
        vh = VoteHistory()
        vh.account_id = self.account_id
        vh.answer_id = self.answer_id
        vh.timestamp = self.timestamp
        vh.position_raw = self.position_raw
        vh.latitude = self.latitude
        vh.longitude = self.longitude

        return vh


question_tag = Table('question_tag', Base.metadata,
                     Column('question_id', ForeignKey('question.id'), primary_key=True),
                     Column('tag_id', ForeignKey('tag.id'), primary_key=True)
                     )

class Tag(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String(128))

    def __init__(self, name=None):
        """

        Arguments:
        - `self`:
        - `name`:
        """
        if name is not None: self.name = name



def _tag_find_or_create(tag_name):
    tag = Tag.query.filter_by(name=tag_name).first()
    if not(tag):
        tag = Tag(name=tag_name)
        # if aufoflush=False used in the session, then uncomment below
        #session.add(tag)
        #session.flush()
    return tag


class Question(Base):
    id = Column(Integer, primary_key=True)
    added = Column(DateTime(), default=sa.sql.func.now())
    removed = Column(DateTime())
    text = Column(String(128))
    answers = relationship("Answer", lazy="joined", order_by="Answer.id",
                           backref=backref("question", lazy="joined"))
    tags = relationship("Tag", secondary=question_tag, lazy="joined")
    owner_id = Column(ForeignKey('account.id'))
    owner = relationship("Account", backref="questions")
    private = Column(Boolean())
    active = Column(Boolean())

    tag_list = association_proxy('tags', 'name',
                                 creator=_tag_find_or_create)
    answer_list = association_proxy('answers', 'text')


    def __init__(self, text=None, answers=None):
        """

        Arguments:
        - `text`: question text
        - `answers`: list of answer text strings
        """
        if text is not None: self.text = text
        if answers is not None: self.answers = answers
        self.active = True
        self.private = False


class Answer(Base):
    id = Column(Integer, primary_key=True)
    text = Column(String(128))
    question_id = Column(ForeignKey('question.id'))

    voters = association_proxy('votes', 'account',
                               creator=lambda account: Vote(account=account, answer=None))


    def __init__(self, text=None):
        """

        Arguments:
        - `answers`: answer text string
        """
        if text is not None: self.text = text













