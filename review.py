import os
import datetime

class Review:
    reviews=[]
    def __init__(self, id, text):
        self.idUser = id
        self.text = text
        self.date = datetime.datetime.now()
    def setID(self,id):
        self.idUser=id
    def getID(self):
        return self.idUser
    def setText(self,text):
        self.text=text
    def getText(self):
        return self.text
    def getDate(self,date):
        return self.date

listReviews=[]

#null User
listReviews.append(Review(0, "text"))

def findUserByID(id):
    global listUsers
    for user in listUsers:
        if(user.id == id):
            return user
    return "No user found"

def findUserByUsername(username):
    global listUsers
    for user in listUsers:
        if(user.username == username):
            return user
    return "No user found"
