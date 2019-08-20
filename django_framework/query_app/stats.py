from pyspark import SparkContext, SparkConf
import jieba
import requests
import datetime
from django.http import HttpRequest

# IMPORTANT: need text files ready in order to use this script
# chinese text segmentation
def segment(filename, output):
    file = open(filename, "r")
    chinese = file.read()
    file.close()
    seg_list = jieba.cut(chinese, cut_all=False)
    list = "/ ".join(seg_list)
    file = open(output, "w")
    file.write(list)
    file.close()

# word count with text files
# returns dictionary with all word counts
def word_count(sc, input):
    text_file = sc.textFile(input)
    map = text_file.flatMap(lambda line: line.split("/ "))
    words = map.map(lambda word: (word, 1))
    count = words.reduceByKey(lambda a, b: a+b)
    sortedCount = count.sortBy(lambda a: -a[1])
    sortedCount.saveAsTextFile("counts") #beware of FileAlreadyExists exception
    result = dict()
    for i in sortedCount.collect():
        result[i[0]] = i[1]
    return result

# WEEKLY SENTIMENT: you need to also run load_emails.py with a filter for the past week along with this
def __main__():
    conf = SparkConf().setAppName("Word Count")
    sc = SparkContext.getOrCreate(conf=conf)
    filename = "/Users/clarence/Documents/data-ingestion/django_framework/query_app/all_emails.txt"
    output_file = "chinese_tokens.txt"
    segment(filename, output_file)
    counts = word_count(sc, output_file)
    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(days=7)
    range = '{ "query": { "bool": { "filter": [ { "range" : { "date" : { "gte": "'+ str(start_time) +'", "lte": "'+ str(end_time) +'", "format": "date_time_no_millis" } } } ] } }, "sort": [ { "date": { "order": "asc" } } ] }'
    data = list()
    data.append(counts)
    data.append(range)
    return data