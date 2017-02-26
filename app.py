#!/usr/bin/python

import sys
import os.path

from functools import wraps

from flask import Flask, g, render_template, redirect, request
from flask_login import login_required, current_user, login_user, logout_user
from flask_bcrypt import Bcrypt

from util.database import *

# 5000 seems a bit... basic. Feel free to change later to something more
#      interesting.

SITE_PORT = 5000

# If testing on localhost, set to True
# Otherwise if running on server, set to False
SERVER_LOCAL = True

# Init app
app = Flask(__name__)

# Setup bcrypt
bcrypt = Bcrypt(app)

# Initialize SQL database
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
db.init_app(app)

# Setup login manage
login_manager.init_app(app)

##### Other constants

RESPONSE_SUCCESS = "success"


# Run before first request: We cannot create all inline
#          (unless we do db = SQLAlchemy(app) )
@app.before_first_request
def initialize_database():
    print "Initialized"
    db.create_all()
    
@app.route("/")
def route_default():
    return redirect("/home")

@app.route("/home")
def route_home():
    return render_template("home.html")

@app.route("/scout")
@login_required
def route_scout():
    return render_template("scout.html")

# Checks for login
@app.route("/login", methods=["POST"])
def route_login_post():
    print "Users"
    print User.query.all()
    # Login user.
    validation = request.form
    user = load_user(validation["email"])
    # If no email or invalid password, return valid error
    print "logging in"
    if not user:
        return "email,Email not found"
    if not bcrypt.check_password_hash(user.password, validation["password"]):
        return "password,Invalid password"
    # Otherwise user login was successful
    user.authenticated = True
    db.session.add(user)
    db.session.commit()
    login_user(user, remember=True)
    print "SUCCESS"
    # Login success
    return RESPONSE_SUCCESS


@app.route("/logout")
@login_required
def route_logout():
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return redirect("/home")

# Registers user
@app.route("/register", methods=["POST"])
def route_register():
    form = request.form
    if ( form["email"] == "" ):
        return "email,Email required"
    if ( load_user( form["email"] ) ):
        return "email,Email already exists"
    if ( form["email"].find("@") == -1 or form["email"].find(".com") == -1):
        return "email,Not a valid email"
    if ( form["password"] == "" ):
        return "password,Password is required"
    if ( form["name"] == "" ):
        return "name,Name is required"
    if ( form["team"] == "" ):
        return "team,Team is required"
    if ( int(form["team"]) <= 0 ):
        return "team,Invalid team number"

    # If none of the checks returned an error, we're good.
    print "ok1"
    user = User(email=form["email"], 
                password=bcrypt.generate_password_hash(form["password"]),
                name=form["name"],
                teamNumber=int(form["team"])
                )
    print "ok4"
    db.session.add(user)
    db.session.commit()
    print "ok5 we done"
    return RESPONSE_SUCCESS

# Login page
@app.route("/login", methods=["GET"])
def route_login_page():
   return render_template("login.html") 

# Register page
@app.route("/register", methods=["GET"])
def route_register_page():
    return render_template("register.html");

# Context Processor, automatically passing data to EVERY template
# Makes sure we don't have to manually pass data every time we render
@app.context_processor
def inject_data_for_all_templates():
    return dict(
            #user=current_user
            )

# Login wrapper. If no user exists, redirect to '/login' 
def login_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if g.user is None:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

# Gets and sets the secret key from a file
def set_secret_key(fname):
    try:
        app.config["SECRET_KEY"] = unicode(open(fname, "rb").read())
    except IOError:
        print "Error: No secret key. Create it with:"
        if not os.path.isdir(os.path.dirname(fname)):
            print "mkdir", os.path.dirname(fname)
        print 'head -c 24 /dev/urandom >', fname
        print "And fill it in with the secret key"
        print "If flask user_login is giving you issues with this, \
               just generate your own random key by mashing the keyboard \
               until you have 32 random characters"
        sys.exit(1)

if __name__ == "__main__":
    if SERVER_LOCAL:
        host = "127.0.0.1"
    else:
        host = "0.0.0.0"
 
    set_secret_key("secret/secretkey")

    app.run(host = host,
            port = SITE_PORT,
            debug = True
            )

