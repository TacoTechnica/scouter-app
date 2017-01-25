#!/usr/bin/python

from flask_login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

login_manager = LoginManager()

# User.
# email, password, authenticated (once user responds with email)
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
def load_user(user_id):
    return User.query.get(user_id)
