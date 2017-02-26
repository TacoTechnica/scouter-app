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
    name = db.Column(db.String)
    teamNumber = db.Column(db.Integer)
    authenticated = db.Column(db.Boolean, default=False)

    def __init__(self, email, password, name, teamNumber):
        self.email = email
        self.password = password
        self.name = name
        self.teamNumber = teamNumber

    def is_active(self):
        return True

    def get_id(self):
        return self.email
    
    def is_authenticated(self):
        return self.authenticated

    # Required by flask logout_user()
    def is_anonymous(self):
        return False


# given user, return user object
@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(user_id)
    except:
        return None


# Team
# Team with its own number and a list of members and admins
class Team(db.Model):

    __tablename__ = "team"

    number =  db.Column(db.Integer, primary_key=True)
    members = db.Column(ScalarListType())
    admins =  db.Column(ScalarListType())


# Sheet
# Test for now...
class Sheet(db.Model):

    __tablename__ = "sheet"

    id = db.Column(db.Integer, primary_key=True)

    team = db.Column(db.Integer)
    
    quality1 = db.Column(db.Integer)
    quality2 = db.Column(db.Boolean)
    quality3 = db.Column(db.String)

    notes =    db.Column(db.String)

