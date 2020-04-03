import os

class User:
    reviews=[]
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password
    def setID(self,id):
        self.id=id
    def getID(self):
        return self.id
    def setUsername(self,username):
        self.username=username
    def getUsername(self):
        return self.username
    def setPassword(self,password):
        self.id=id
    def getPassword(self):
        return self.password


listUsers=[]

#null User
listUsers.append(User(0, "null", "null"))

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
