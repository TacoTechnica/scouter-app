#!/usr/bin/python

import sys
import os.path

from functools import wraps

from flask import Flask, g, render_template, redirect, request
from flask_login import login_required, current_user
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

# Run before first request: We cannot create all inline
#          (unless we do db = SQLAlchemy(app) )
@app.before_first_request
def initialize_database():
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
    # Login user.
    validation = request.form
    email = user_loader(validation["email"])
    # If no email or invalid password, return valid error
    print "logging in"
    if not email:
        return "email,Email not found"
    if not bcrypt.check_password_hash(user.password, validation["password"]):
        return "password,Invalid password"
    # Otherwise user login was successful
    user.authenticated = True
    db.session.add(email)
    db.session.commit()
    login_user(email, remember=True)
    print "SUCCESS"
    # Login success
    return "1"


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
    # If user already exists
    if (user_loader(validation["email"])):
        return "email,Email already exists"
 
    # If none of the checks returned an error, we're good.
    user = User(email=validation["email"], 
                password=bcrypt.generate_password_hash(validation["password"]) )
    db.session.add(user)
    db.session.commit()
    return "1"

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
        app.config["SECRET_KEY"] = open(fname, "rb").read()
    except IOError:
        print "Error: No secret key. Create it with:"
        if not os.path.isdir(os.path.dirname(fname)):
            print "mkdir", os.path.dirname(fname)
        print 'head -c 24 /dev/urandom >', fname
        print "And fill it in with the secret key"
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

