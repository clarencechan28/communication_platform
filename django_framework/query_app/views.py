from django.http import HttpResponse
import os
import requests
import json
import re
from snownlp import SnowNLP, sentiment
import jieba
from flask import Flask, render_template
import datetime
from . import stats

# Function that calculates the average sentiment of a word based on the SnowNLP model.
# Returns float representing average sentiment
def get_average_sentiment(text):
    if text:
        snow = SnowNLP(text)
        average = 0
        count = 0
        words = snow.words
        for item in words:
            s = SnowNLP(item)
            average += s.sentiments
            count += 1
        return average/count
        
# Parses a string to only retrieve the chinese characters in the string
def getChinese(context):
    # context = context.decode("utf-8") # convert context from str to unicode
    filtrate = re.compile(u'[^\u4E00-\u9FA5]') # non-Chinese unicode range
    context = filtrate.sub(r'', context) # remove all non-Chinese characters
    context = context.encode("utf-8") # convert unicode back to str
    return context

# Returns only the email bodies from all of the JSON data for each email in the elasticsearch database
def getEmailBody(jsonOutput):
    emails = []
    emailMessage = ""
    #Generate emails
    readeableJSON = json.loads(jsonOutput.text)
    for emailData in readeableJSON["hits"]["hits"]:
        for details in emailData["_source"]:
            if details == "msg_body":
                emailMessage = emailData["_source"][details]
                emails.append([emailMessage])
    return emails

# Determines the keyword associated with the highest or lowest sentiment
# Returns list with the key value pair associated with the max or min sentiment
def maxNmin(data, str):
    result = list()
    max_key = ""
    min_key = ""
    if(str == "max"):
        max = 0
        for key in data:
            if data.get(key, "none"):
                if(data.get(key, "none") > max):
                    max = data.get(key, "none")
                    max_key = key
        result.append(max_key)
        result.append(max)
    elif(str == "min"):
        min = 1
        for key in data:
            if data.get(key, "none"):
                if(data.get(key, "none") < min):
                    min = data.get(key, "none")
                    min_key = key
        result.append(min_key)
        result.append(min)
    return result

# Main function that processes the HTTP request
def index(request, bool):
    q = request.GET.get("q", None)
    result = ""
    limit = 0
    if q:
        if bool == 't':
            properties = stats.__main__() # use stats.py functionality
            words = properties[0] # word count data
            vals = dict()
            headers = {
                'Content-Type': 'application/json',
            }
            response = requests.get('http://localhost:9200/comm_platform_via_python/_search?q=%s' % q, headers=headers, data=properties[1])
            # only bodies
            response = getEmailBody(response)
            for text in response:
                chinese = getChinese(text[0]).decode('utf-8')
                #only chinese and sentiment
                result += "Body: " + chinese
                result += "<br />"
                result += "Average Sentiment: " + str(get_average_sentiment(chinese))
                result += "<br />"
            for word in words:
                vals[word] = get_average_sentiment(word) # store every value and associated sentiment in map
            result += "List of most common words and their sentiments: "
            result += "<br />"
            for key, val in vals.items():
                if limit < 25 and key: # null string check 
                    result += key + ": " + str(val)
                    result += "<br />"
                    limit += 1
                else: 
                    break
            maximum = maxNmin(vals, "max")
            minimum = maxNmin(vals, "min")
            result += "Highest sentiment keyword: " + maximum[0] + " - " + str(maximum[1])
            result += "<br />"
            result += "Lowest sentiment keyword: " + minimum[0] + " - " + str(minimum[1])
            result += "<br />"
        else:
            headers = {
                'Content-Type': 'application/json',
            }
            response = requests.get('http://localhost:9200/comm_platform_via_python/_search?q=%s' % q, headers=headers)
            # only bodies
            response = getEmailBody(response)
            for text in response:
                chinese = getChinese(text[0]).decode('utf-8')
                #only chinese and sentiment
                result += "Body: " + chinese
                result += "<br />"
                result += "Average Sentiment: " + str(get_average_sentiment(chinese))
                result += "<br />"
        return HttpResponse(result)
    else:
        return HttpResponse('HTTP GET request required')

# handling a 404 error
app = Flask(__name__)
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")