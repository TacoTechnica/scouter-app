#!/usr/bin/python

import sys
import os.path

from flask import Flask, g, render_template, redirect
from flask_login import login_required, current_user
from flask.ext.bcrypt import Bcrypt

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
    validation = request.args
    print validation
    user = user_loader(validation["email"])
    if user and bcrypt.check_password_hash(user.password, validation["password"]):
        #user.authenticated = True
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=True)
        # Login success
        return True
    # Login failed
    return False

# Login page
@app.route("/login", methods=["GET"])
def route_login_get():
   return render_template("login.html") 

@app.route("/logout")
@login_required
def route_logout():
    logout_user()
    return redirect("/home")

# Login wrapper. If no user exists, redirect to '/login' 
def login_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if g.user is None:
            return redirect('login')
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

