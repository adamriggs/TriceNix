

#-----------------
# imports
#-----------------

from twitter import *
import MySQLdb
import json
import eliza
import nltk, re, pprint
from nltk import *

#-----------------
# main variables
#-----------------

with open("keys.json") as data_file:
    data = json.load(data_file)

twitter = Twitter(auth=OAuth(data["keys"]["token"], data["keys"]["token_key"], data["keys"]["con_secret"], data["keys"]["con_secret_key"])) 
database = MySQLdb.connect(host=data["database"]["host"],  user=data["database"]["user"], passwd=data["database"]["passwd"], db=data["database"]["db"])
cursor = database.cursor()
database.close()

screenNames = ["adamriggs"]
therapist = eliza.eliza()
atMentions = []
hashTags = []
urls = []

response = twitter.statuses.user_timeline(screen_name=screenNames[0])
mentions = twitter.statuses.mentions_timeline()

#-----------------
# functions
#-----------------

def connectDB():
    global database
    global cursor
    database = MySQLdb.connect(host=data["database"]["host"],  user=data["database"]["user"], passwd=data["database"]["passwd"], db=data["database"]["db"])
    cursor=db.cursor()

def closeDB():
    global database
    database.close()
    
def checkDBForID(id):
    global database
    global cursor
    
    connectDB()
    closeDB()
    
def insertIDIntoDB(id):
    global database
    global cursor
    
    connectDB()
    closeDB()

def removeNonWords(message):
    words = message.split()
    prevW = ""
    newMessage = ""
    
    if(words[0][:1]=="."):
        words[0]=words[0][1:]
        
    for w in words:
        if (w[:1] != "@") and (w[:1] != "#") and (w[:4].lower() != "http"):
            #print(w)
            if prevW[:1] == "@":
                #print(prevW)
                newMessage += prevW + " "
            if prevW[:1] == "#":
                #print(prevW)
                newMessage += prevW + " "
            newMessage += w + " "
        elif w[:1] == "@":
            if(w.lower() != "@tricenix"):
                atMentions.append(w)
        elif w[:1] == "#":
            hashTags.append(w)
        elif w[:4] == "http":
            urls.append(w)
        prevW = w
    return newMessage

def createElizaInput(taggedArray):
    #print(taggedArray)
    verb_found = False
    noun_found = False
    noun = ""
    output = ""
    for tag in taggedArray:
        
        if(tag[1][:2] == ("NN" or "PR" or "IN")):
            print('*****noun found')
            noun_found = True
            noun = tag[0]
            print(tag[0])
        
        if(tag[1][:2] == "VB" and noun_found == True and verb_found == False):
            print(tag[0])
            output = noun + " " + tag[0]
            verb_found = True
    print("\n"+output+"\n")
    return output



# massage tweet data
post = response[0]['text']
#print(post)
newPost = removeNonWords(post)
tokens = word_tokenize(post)
#tokens_punct = wordpunct_tokenize(post)
words = [w.lower() for w in tokens]
tagged = nltk.pos_tag(words)



# output massaged data
#print(response[0])
print("\n\n")
print(response[0]['id'])
print(newPost)
print("\n\n")
#print(tagged)
#print("\n\n")
#print(therapist.respond(createElizaInput(tagged)))
message = therapist.respond(newPost)
message = "@" + screenName + " " + message
messageLen = len(message)
if messageLen < 140:
    for h in hashTags:
        if messageLen + 1 + len(h) < 140:
            message += " " + h
            messageLen = len(message)
    for a in atMentions:
        if messageLen + 1 + len(a) < 140:
            message += " " + a
            messageLen = len(message)
print(message)
print("\n\n")

#t.statuses.update(status=message, in_reply_to_status_id=response[0]['id'])

