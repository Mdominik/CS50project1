import os
from flask import Flask, session, render_template, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
import csv
from sqlalchemy.orm import scoped_session, sessionmaker
import requests

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f=open("books.csv")
    reader=csv.reader(f)
    counter=0
    for isbn,title,author,year in reader:
        db.execute("INSERT INTO books (isbn,title,author,year) VALUES (:isbn,:title,:author,:year)",
        {"isbn":isbn, "title":title, "author":author, "year":year})
        counter = counter+1
        print(f"Added book nr {counter} isbn: {isbn}")
    db.commit()
main()
