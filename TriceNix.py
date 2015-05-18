from twitter import *
import json
import eliza
import nltk, re, pprint
from nltk import *

with open("keys.json") as data_file:
    data = json.load(data_file)

t=Twitter(auth=OAuth(data["keys"]["token"], data["keys"]["token_key"], data["keys"]["con_secret"], data["keys"]["con_secret_key"])) 

response = t.statuses.user_timeline(screen_name="adamriggs")
therapist = eliza.eliza()
atMentions = []
hashTags = []
urls = []

def removeNonWords(message):
    #words = message.lower()
    words = message.split()
    prevW = ""
    #print(words)
    newMessage = ""
    
    if(words[0][:1]=="."):
        words[0]=words[0][1:]
        
    for w in words:
        #print(w[:4].lower() == "http")
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
            atMentions.append(w)
        elif w[:1] == "#":
            hashTags.append(w)
        elif w[:4] == "http":
            urls.append(w)
        prevW = w
    #print(atMentions)
    #print(hashTags)
    #print(urls)
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
#post = "This week I'll be hiding Luis Tiant bobbleheads in Boston - each bobblehead = 2 @RedSox tix to Luis Tiant Bobblehead Night on Thur at Fenway"
#print(post)
newPost = removeNonWords(post)
tokens = word_tokenize(post)
#tokens_punct = wordpunct_tokenize(post)
words = [w.lower() for w in tokens]
tagged = nltk.pos_tag(words)



# output massaged data
print("\n\n")
print(response[0]['id'])
print(newPost)
print("\n\n")
#print(tagged)
#print("\n\n")
#print(therapist.respond(createElizaInput(tagged)))
message = therapist.respond(newPost)
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

t.statuses.update(status=message, in_reply_to_status_id=response[0]['id'])

