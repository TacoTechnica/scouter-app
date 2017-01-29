#!/usr/bin/python

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy #flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy_utils import ScalarListType

db = SQLAlchemy()

login_manager = LoginManager()

# User
# email, password, authenticated (once user logins)
class User(db.Model):
    
    __tablename__ = "user"
    
    email = db.Column(db.String, primary_key=True)
    password = db.Column(db.String)
    authenticated = db.Column(db.Boolean, default=False)

    def get_id(self):
        return self.email
    
    def is_authenticated(self):
        return self.authenticated


# given user, return user object
@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)

# Team
# Team with its own number and a list of members and admins
class Team(db.Model):

    __tablename__ = "team"

    number =  db.Column(db.Integer, primary_key=True)
    members = db.Column(ScalarListType())
    admins =  db.Column(ScalarListType())
