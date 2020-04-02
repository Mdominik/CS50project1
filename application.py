import os
from user import *
from flask import Flask, session, render_template, request, jsonify,redirect
from flask_session import Session
from sqlalchemy import create_engine

from sqlalchemy.orm import scoped_session, sessionmaker
import requests

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
db_session=Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "6fHbYVtE5pAhvv6MTXk0Q", "isbns": "9781632168146"})


#storing all existing users in a dictionary. {username : [id, password, reviews]}
userCounter=0

def noOneLoggedIn():
    return session["id"]==0

@app.route("/")
def index():
    #return jsonify(res.json())
    return render_template("homepage.html", loginFailed=False, user=findUserByID(session["id"]))

@app.route("/signedUp", methods=["POST"])
def signedup():
    global userCounter,listUsers
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = findUserByUsername(username)
        if user == "No user found":
            userCounter+=1
            listUsers.append(User(userCounter, username, password))
            session["id"] = userCounter
        else:
            return render_template("signup.html", accountExists=True, user=findUserByID(session["id"]))
        return render_template("bookSearch.html", user=findUserByID(session["id"]))

@app.route("/signup")
def signup():
    if(noOneLoggedIn()):
        return render_template("signup.html",accountExists=False)
    else:
        return redirect("/", code=302)


@app.route("/signout")
def signout():
    session["id"] = 0
    return render_template("homepage.html", loginFailed=False, user=findUserByID(session["id"]))


@app.route("/loggedIn", methods=["POST"])
def loggedIn():
    username = request.form.get("username")
    password = request.form.get("password")
    user = findUserByUsername(username)

    if user == "No user found":
        return render_template("login.html", loginFailed=True)
    if user.getUsername() == username and user.getPassword() == password:
        session["id"] = user.getID()
        return render_template("bookSearch.html", user=findUserByID(session["id"]))
    else:
        return render_template("login.html", loginFailed=True)
    return render_template("error.html")

@app.route("/login")
def login():
    if(noOneLoggedIn()):
        return render_template("login.html", loginFailed=False)
    else:
        return redirect("/", code=302)

@app.route("/book-query", methods=["GET","POST"])
def bookQuery():
    if(not noOneLoggedIn()):
        try:
            if request.method == "POST":
                title = request.form.get("title")
                author = request.form.get("author")
                isbn = request.form.get("isbn")
                books = db.execute("SELECT * FROM books WHERE title = :title OR isbn = :isbn",
                                  {"title": title, "isbn": isbn}).fetchall()
                if len(books)==0:
                    return render_template("bookSearch.html", bookNotFound=True, user=findUserByID(session["id"]))
                db.commit()
                return render_template("bookRecord.html", books=books, user=findUserByID(session["id"]))
            elif request.method == "GET":
                return render_template("bookSearch.html", bookNotFound=False, user=findUserByID(session["id"]))
        except:
            db_session.rollback()
    else:
        return redirect("/", code=302)
