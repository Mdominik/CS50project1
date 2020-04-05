import os
from user import *
from review import Review
from flask import Flask, session, render_template, request, jsonify,redirect
from flask_session import Session
from sqlalchemy import create_engine
import datetime

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


#find highest session in the database to be up to date with id SERIAL KEY
def getHighestSessionID():
    id = db.execute("SELECT id FROM users ORDER BY id DESC LIMIT 1").fetchone()
    db.commit()
    for i in id:
        #print(i)
        return i

#find a user in the database
def findUserByID():
        user = db.execute("SELECT * FROM users WHERE id = :id", {"id" : session["id"]}).fetchone()
        db.commit()
        return user

def findUserByUsername(username):
        user = db.execute("SELECT * FROM users WHERE username = :username", {"username" : username}).fetchone()
        db.commit()
        return user

#find reviews by isbn
def getReviewsByISBN(isbn):
    reviews = db.execute("SELECT * FROM reviews WHERE isbn = :isbn", {"isbn":isbn}).fetchall()
    db.commit()
    return reviews

def getBookByISBN(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn":isbn}).fetchone()
    db.commit()
    return book

def someoneLoggedIn():
    return session["id"] is not 0

@app.route("/")
def index():
    #return jsonify(res.json())
    print("Session in homepage:")
    print(session["id"])
    if someoneLoggedIn():
        user = findUserByID()
        return render_template("homepage.html", loginFailed=False, user=user)
    else:
        return render_template("homepage.html", loginFailed=False, user=None)

#page showed after pressing submit in signup form
@app.route("/signedUp", methods=["POST"])
def signedup():
    if request.method == "POST":

        #get the parameters from form and check for the user in database
        username = request.form.get("username")
        password = request.form.get("password")
        user = findUserByUsername(username)

        #if the user doesnt exist, create him
        if  user is None:
            db.execute("INSERT INTO users (username,password) VALUES (:username, :password)",
            {"username":username, "password":password})
            db.commit()
            user = findUserByUsername(username)

            session["id"] = getHighestSessionID()
            return render_template("bookSearch.html", user=user)

        #if the user exists, show account exist error
        else:
            return render_template("signup.html", accountExists=True, user=user)


#signup form
@app.route("/signup")
def signup():
    #only show the signup form if no one is logged in`
    if(not someoneLoggedIn()):
        return render_template("signup.html",accountExists=False)

    #if someone is logged in, don't allow to show signup and redirect to homepage
    else:
        return redirect("/", code=302)

#after pressing signout button. Session will be 0 and render homepage
@app.route("/signout")
def signout():
    session["id"] = 0
    return render_template("homepage.html", loginFailed=False, user=None)

#page after logging in
@app.route("/loggedIn", methods=["POST"])
def loggedIn():

    #get the variables from login form
    username = request.form.get("username")
    password = request.form.get("password")

    #search for the row in users database matching username and password
    user = db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username" : username, "password":password}).fetchone()
    db.commit()

    #if no user found, show loginFailed
    if user is None:
        return render_template("login.html", loginFailed=True)

    #if user found, show book search form
    else:
        session["id"] = user.id
        return render_template("bookSearch.html", user=user)

#login form
@app.route("/login")
def login():

    #show the login form only if no one is logged in (session is 0)
    if(not someoneLoggedIn()):
        return render_template("login.html", loginFailed=False)

    #if someone is logged in, dont show the login form and redirect to homepage
    else:
        return redirect("/", code=302)

#searching book form
@app.route("/book-query", methods=["GET","POST"])
def bookQuery():
    if(someoneLoggedIn()):
        if request.method == "POST":

            #fetch variables from the form
            title = request.form.get("title")
            author = request.form.get("author")
            isbn = request.form.get("isbn")

            #select all possible records
            query = "SELECT * FROM books WHERE title LIKE '%%%s%%' AND isbn LIKE '%%%s%%'" % (title, isbn)
            books = db.execute(query).fetchall()
            db.commit()

            #get the current user based on the session
            user = findUserByID()

            #if book list is empty, return books not found
            if books is []:
                return render_template("bookSearch.html", bookNotFound=True, user=user)

            #if book found, return books
            return render_template("bookRecord.html", books=books, user=user)
        elif request.method == "GET":

            #get the current user based on the session
            user = findUserByID()
            return render_template("bookSearch.html", bookNotFound=False, user=user)
    else:
        return redirect("/", code=302)

@app.route("/book/<string:isbn>", methods=["GET","POST"])
def book(isbn):
    title=request.args.get('title')
    author=request.args.get('author')
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "6fHbYVtE5pAhvv6MTXk0Q", "isbns": isbn})
    book = getBookByISBN(isbn)

    avg_rating_goodreads = res.json()["books"][0]["average_rating"]


    reviews = getReviewsByISBN(isbn)

    #db.execute("INSERT INTO mybooks (isbn,title,year,author) VALUES (:isbn,:title,:year,:rating,:numberComments)",
    #{"isbn":book.isbn, "title":book.title,"year":book.year,"rating":0,"numberComments":0})

    #db.commit()

    #find current user
    user = findUserByID()


    #get book from goodreads preloaded table
    book = getBookByISBN(isbn)
    print("ALL REVIEWS:")
    print(reviews)
    #
    our_average_rating=0.0




    if request.method == "GET":
        #select book's reviews
        pass

    elif request.method == "POST":
        comment = request.form.get("comment")
        rating = request.form.get("myBookRating")
        #print(comment)
        print(rating)

        db.execute("INSERT INTO reviews (iduser,isbn,rating,comment,date) VALUES (:iduser,:isbn,:rating,:comment,:date)",
        {"iduser":session["id"],"isbn":book.isbn,"rating":rating,"comment":comment,"date":datetime.datetime.now()})
        db.commit()

    #select book's reviews
    reviews = getReviewsByISBN(isbn)

    for review in reviews:
        our_average_rating = our_average_rating + float(review["rating"])

    try:
        our_average_rating = our_average_rating / len(reviews)
    except ZeroDivisionError:
        our_average_rating=0

    books = db.execute("SELECT * FROM reviews WHERE iduser = :iduser ", {"iduser":session["id"]}).fetchall()
    db.commit()
    reviewWritten = books is []

    return render_template("book.html", book=book, goodReadsRating = float(avg_rating_goodreads), our_average_rating = our_average_rating,  user=user, reviews=reviews, reviewWritten=reviewWritten)
