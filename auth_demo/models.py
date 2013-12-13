import json
from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    String,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


### DEFINE MODEL
class User(Base):
    __tablename__='users'
    id=Column(Integer, primary_key=True)
    login=Column(String)
    password=Column(String)
    groups=Column(String)

    def __init__(self, login, password, groups=None):
        self.login = login
        self.password = password
        self.groups = json.dumps(groups or [])

    def check_password(self, passwd):
        return self.password == passwd

class Page(Base):
    __tablename__='pages'
    id=Column(Integer, primary_key=True)
    title=Column(String)
    uri=Column(String)
    body=Column(String)
    owner=Column(String)

    def __init__(self, title, uri, body, owner):
        self.title = title
        self.uri = uri
        self.body = body
        self.owner = owner
