# Data Ingestion with Elasticsearch and Sentiment Analysis API
Purpose: Load email data from the Exaleap email archive hosted by Microsoft Outlook into Elasticsearch for querying and to perform bilingual sentiment analysis on the email text. Each element and header of each individual email will be indexed accordingly in Elasticsearch.

## Install Dependencies
### Python dependencies 
The libraries you will need to install are email, bs4, elasticsearch, imaplib, snownlp, django, json, re, and requests. Pip installing these libraries is highly recommended.
```
pip3 install -r requirements.txt
```

### Elasticsearch dependences
The API library assumes that you are already running an instance of Elasticsearch locally. To run an elasticsearch instance, simply run
```
cd elasticsearch-7.1.0
bin/elasticsearch
```
## Usage
### Email Ingestion
load_emails.py is the main program that loads the emails into your Elasticsearch instance from the server after prompted with the username and password. To run the program, simply call
```
python3 load_emails.py
```
Note: In the load_emails.py script, I create text file to help collect statistics, which I have omitted in this repository. The file will be in a different directory than stats.py, which can cause problems because the script needs to directly read the file in order to calculate statistics. Please move the resulting text file from this script to the /django_framework/query_app/ for correct functionality.

### Django Server (main app)
The Django framework assists in creating HTTP requests to query email bodies from the Elasticsearch database with keywords.
To run the Django instance, run this command:
```
cd django_framework
python3 manage.py runserver
```
You can use the Django instance in your browser with the URL: http://localhost:8000/query_app/f/?q=
where the keyword is inputted at the end of the URL. The additional element, "f", is a parameter for the request to exclude the statistics, which will be covered further in detail below.

## Weekly Sentiment
stats.py contains code for segmentation of chinese words and word counting with Apache Spark. You can run the script alongside the HTTP request through Django by using this query: http://localhost:8000/t/query_app/?q=. As explained earlier, the "f" in the url indicates that the sentiment calculations are excluded, while "t" indicates that updated sentiment calculations are included.