import os

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

isLoggedin=False

#storing all existing users in a dictionary. {username : [id, password, reviews]}
listExistingUsers={}
userCounter=0
listLoggedUsers={}
listReviews={}
listReviews["username"]=[]

class User:
    def __init__(self, id, surname, reviews):
        self.id = id
        self.surname = surname
        self.reviews = reviews
    def findUserByID(id):
        


@app.route("/")
def index():
    #return jsonify(res.json())
    return render_template("homepage.html", loginFailed=False, id=session["id"])

@app.route("/signedUp", methods=["POST"])
def signedup():
    global userCounter
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username not in listExistingUsers:
            userCounter+=1
            listExistingUsers[username] =  [userCounter, password]
            session["id"] = userCounter
        else:
            return render_template("signup.html", accountExists=True, id=session["id"])
        return render_template("bookSearch.html", username=username, id=session["id"])

@app.route("/signup")
def signup():
    if(session["id"]==0):
        return render_template("signup.html",accountExists=False)
    else:
        return redirect("/", code=302)


@app.route("/signout")
def signout():
    session["id"] = 0
    return render_template("homepage.html", loginFailed=False, id=session["id"])


@app.route("/loggedIn", methods=["POST"])
def loggedIn():
    try:
        username = request.form.get("username")
        password = request.form.get("password")
        rememberMe = request.form.get("remember-me")
        if username in listExistingUsers and listExistingUsers[username][1]==password:
            session["id"] = listExistingUsers[username][0]
            listLoggedUsers[username]=[userCounter, password]
            return render_template("bookSearch.html", username=username, id=session["id"])
        return render_template("login.html", loginFailed=True, id=session["id"])
    except:
        db_session.rollback()

@app.route("/login")
def login():
    if(session["id"]==0):
        return render_template("login.html", loginFailed=False, id=session["id"])
    else:
        return redirect("/", code=302)

@app.route("/book-query", methods=["GET","POST"])
def bookQuery():
    if(session["id"]!=0):
        try:
            if request.method == "POST":
                title = request.form.get("title")
                author = request.form.get("author")
                isbn = request.form.get("isbn")
                books = db.execute("SELECT * FROM books WHERE title = :title OR isbn = :isbn",
                                  {"title": title, "isbn": isbn}).fetchall()
                if len(books)==0:
                    return render_template("bookSearch.html", bookNotFound=True, id=session["id"])
                db.commit()
                return render_template("bookRecord.html", books=books, id=session["id"])
            elif request.method == "GET":
                return render_template("bookSearch.html", bookNotFound=False, id=session["id"])
        except:
            db_session.rollback()
    else:
        return redirect("/", code=302)
