import os
from user import *
from review import Review
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

#user's id
userCounter=0

def getHighestSessionID():
    id = db.execute("SELECT id FROM users ORDER BY id DESC LIMIT 1").fetchone()
    db.commit()
    for i in id:
        print(i)
        return i

def noOneLoggedIn():
    return session["id"]==0

@app.route("/")
def index():
    #return jsonify(res.json())
    print("Session in homepage:")
    print(session["id"])
    if session["id"]!=0:
        user = db.execute("SELECT * FROM users WHERE id = :id", {"id" : session["id"]}).fetchone()
        db.commit()
        return render_template("homepage.html", loginFailed=False, user=user)
    else:
        return render_template("homepage.html", loginFailed=False, user=None)

@app.route("/signedUp", methods=["POST"])
def signedup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = db.execute("SELECT * FROM users WHERE username = :username", {"username" : username}).fetchone()

        db.commit()
        if  user==None:
            db.execute("INSERT INTO users (username,password) VALUES (:username, :password)",
            {"username":username, "password":password})
            db.commit()
            user = db.execute("SELECT * FROM users WHERE username = :username", {"username" : username}).fetchone()
            db.commit()
            session["id"] = getHighestSessionID()
            return render_template("bookSearch.html", user=user)
        else:
            return render_template("signup.html", accountExists=True, user=user)


@app.route("/signup")
def signup():
    if(noOneLoggedIn()):
        return render_template("signup.html",accountExists=False)
    else:
        return redirect("/", code=302)

@app.route("/signout")
def signout():
    session["id"] = 0
    return render_template("homepage.html", loginFailed=False, user=None)


@app.route("/loggedIn", methods=["POST"])
def loggedIn():
    username = request.form.get("username")
    password = request.form.get("password")
    user = db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username" : username, "password":password}).fetchone()
    db.commit()
    if user==None:
        return render_template("login.html", loginFailed=True)
    else:
        session["id"] = user.id
        return render_template("bookSearch.html", user=user)
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
        if request.method == "POST":
            title = request.form.get("title")
            author = request.form.get("author")
            isbn = request.form.get("isbn")
            query = "SELECT * FROM books WHERE title LIKE '%%%s%%' AND isbn LIKE '%%%s%%'" % (title, isbn)
            books = db.execute(query).fetchall()
            db.commit()
            user = db.execute("SELECT * FROM users WHERE id = :id", { "id":session["id"] }).fetchone()
            db.commit()
            if books == []:
                return render_template("bookSearch.html", bookNotFound=True, user=user)
            return render_template("bookRecord.html", books=books, user=user)
        elif request.method == "GET":
            user = db.execute("SELECT * FROM users WHERE id = :id", {"id" : session["id"]}).fetchone()
            db.commit()
            return render_template("bookSearch.html", bookNotFound=False, user=user)
    else:
        return redirect("/", code=302)

@app.route("/book/<string:isbn>", methods=["GET","POST"])
def book(isbn):
    title=request.args.get('title')
    author=request.args.get('author')
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "6fHbYVtE5pAhvv6MTXk0Q", "isbns": isbn})
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn":isbn}).fetchone()
    db.commit()
    #db.execute("INSERT INTO mybooks (isbn,title,year,rating,numberComments) VALUES (:isbn,:title,:year,:rating,:numberComments)",
    #{"isbn":book.isbn, "title":book.title,"year":book.year,"rating":0,"numberComments":0})

    #db.commit()
    user = db.execute("SELECT * FROM users WHERE id = :id", {"id":session["id"]}).fetchone()
    db.commit()
    if request.method == "GET":
        print(book)
        print(user)
        return render_template("book.html", book=book, myRating = 4.5, goodReadsRating = 4.3, numberComments = 3, user=user)
