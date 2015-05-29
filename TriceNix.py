

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
#atMentions = []
#hashTags = []
#urls = []

tweets = twitter.statuses.user_timeline(screen_name=screenNames[0])
tweetsLen = len(tweets)
mentions = twitter.statuses.mentions_timeline()
mentionsLen = len(mentions)
allMessages = []
allMessagesLen = tweetsLen + mentionsLen
#print("tweetsLen == " + str(tweetsLen))
#print("mentionsLen == " + str(mentionsLen))

#-----------------
# functions
#-----------------

def consolidateMessages():
    for msg in tweets:
        allMessages.append({"id": msg['id'], "message":msg['text'], "screen_name": msg['user']['screen_name']})
    for msg in mentions:
        allMessages.append({"id": msg['id'], "message":msg['text'], "screen_name": msg['user']['screen_name']})

def connectDB():
    global database
    global cursor
    database = MySQLdb.connect(host=data["database"]["host"],  user=data["database"]["user"], passwd=data["database"]["passwd"], db=data["database"]["db"])
    cursor=database.cursor()

def closeDB():
    global database
    database.close()
    
def checkDBForID(id):
    global cursor
    cursor.execute("SELECT COUNT(1) FROM tricenix WHERE reply_to_id = \'" + str(id) + "\'")
    msgExists=cursor.fetchone()
    if msgExists[0]:
        return True
    else:
        return False
    
def insertIDIntoDB(msg):
    global database
    global cursor
    msg['response'] = msg['response'].replace('"', r'\"')
    msg['response'] = msg['response'].replace("'", r"\'")
    msg['message'] = msg['message'].replace('"', r'\"')
    msg['message'] = msg['message'].replace("'", r"\'")
    msg['newMessage'] = msg['newMessage'].replace('"', r'\"')
    msg['newMessage'] = msg['newMessage'].replace("'", r"\'")
    msg['atMentions']= ','.join(map(str, msg['atMentions']))
    msg['hashTags']= ','.join(map(str, msg['hashTags']))
    msg['urls']= ','.join(map(str, msg['urls']))
    sql = "INSERT INTO tricenix (reply_to_id, screen_name, message, response, at_mentions, hash_tags, urls) VALUES (\'" + str(msg['id']) + "\', \'" + str(msg['screen_name']) + "\', \'" + str(msg['message'])  + "\', \'" + str(msg['response'])+ "\', \'" + str(msg['atMentions']) + "\', \'" + str(msg['hashTags']) + "\', \'" + str(msg['urls']) + "\')"
    #print(sql)
    cursor.execute(sql)
    database.commit()
    

def removeNonWords(msg):
    newMsg = msg
    words = msg['message'].split()
    prevW = ""
    newText = ""
    atMentions = []
    hashTags = []
    urls = []
    
    if(words[0][:1]=="."):
        words[0]=words[0][1:]
        
    for w in words:
        if (w[:1] != "@") and (w[:1] != "#") and (w[:4].lower() != "http"):
            #print(w)
            if prevW[:1] == "@":
                #print(prevW)
                newText += prevW + " "
            if prevW[:1] == "#":
                #print(prevW)
                newText += prevW + " "
            newText += w + " "
        elif w[:1] == "@":
            if(w.lower() != "@tricenix"):
                atMentions.append(w)
        elif w[:1] == "#":
            hashTags.append(w)
        elif w[:4] == "http":
            urls.append(w)
        prevW = w
    
    newMsg['newMessage'] = newText
    newMsg['atMentions'] = atMentions
    newMsg['hashTags'] = hashTags
    newMsg['urls'] = urls
    
    return newMsg

def createElizaInput(taggedArray):
    #print(taggedArray)
    verb_found = False
    noun_found = False
    noun = ""
    output = ""
    for tag in taggedArray:
        
        if(tag[1][:2] == ("NN" or "PR" or "IN")):
            #print('*****noun found')
            noun_found = True
            noun = tag[0]
            print(tag[0])
        
        if(tag[1][:2] == "VB" and noun_found == True and verb_found == False):
            print(tag[0])
            output = noun + " " + tag[0]
            verb_found = True
    #print("\n"+output+"\n")
    return output



# massage tweet data
#post = tweets[0]['text']
#print(post)
#newPost = removeNonWords(post)
#tokens = word_tokenize(post)
#tokens_punct = wordpunct_tokenize(post)
#words = [w.lower() for w in tokens]
#tagged = nltk.pos_tag(words)


#-----------------
# main loop
#-----------------
consolidateMessages()
#print(allMessages)
connectDB()
print("\n\n")
print(tweets[0]['id'])
for msg in allMessages:
    if checkDBForID(msg['id'])==False:
        msg = removeNonWords(msg)
        msg['response'] = therapist.respond(msg['newMessage'])
        msg['response'] = "@" + msg['screen_name'] + " " + msg['response']
        responseLen = len(msg['response'])
        if responseLen < 140:
            for h in msg['hashTags']:
                if responseLen + 1 + len(h) < 140:
                    msg['response'] += " " + h
                    responseLen = len(msg['response'])
            for a in msg['atMentions']:
                if responseLen + 1 + len(a) < 140:
                    msg['response'] += " " + a
                    responseLen = len(msg['response'])
        #twitter.statuses.update(status=msg['response'], in_reply_to_status_id=msg['id'])
        insertIDIntoDB(msg)
    
# if checkDBForID(tweets[0]['id'])==False:
#     #print(cursor.execute("select * from tricenix"))
#     print(newPost)
#     print("\n\n")
#     #print(tagged)
#     #print("\n\n")
#     #print(therapist.respond(createElizaInput(tagged)))
#     response = therapist.respond(newPost)
#     response = "@" + screenNames[0] + " " + response
#     responseLen = len(response)
#     if responseLen < 140:
#         for h in hashTags:
#             if responseLen + 1 + len(h) < 140:
#                 response += " " + h
#                 responseLen = len(response)
#         for a in atMentions:
#             if responseLen + 1 + len(a) < 140:
#                 response += " " + a
#                 responseLen = len(response)
#     print(response)
#     print("\n\n")
    #twitter.statuses.update(status=response, in_reply_to_status_id=tweets[0]['id'])
    #insertIDIntoDB(tweets[0]['id'], screenNames[0], post, response)

closeDB()


