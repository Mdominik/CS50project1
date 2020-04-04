import os
import requests
class Book:
    reviews=[]


    id=0
    def __init__(self, title, isbn, author, year, rating):
        id+=1
        self.title = title
        self.isbn = isbn
        self.author = author
        self.year = year
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "KEY", "isbns": "9781632168146"})
        res.json()
        self.rating =
    def getID(self):
        return Book.id
    def setTitle(self,title):
        self.username=username
    def getTitle(self):
        return self.username
    def setISBN(self,isbn):
        self.isbn=isbn
    def getISBN(self):
        return self.isbn
    def setAuthor(self,author):
        self.author=author
    def getAuthor(self):
        return self.author
    def setYear(self,year):
        self.year=year
    def getYear(self):
        return self.year

listBooks = []


def findBookByISBN(isbn):
    global listBooks
    for book in listBooks:
        if(book.isbn == isbn):
            return book
    return "No book found"
