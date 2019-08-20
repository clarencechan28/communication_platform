import email
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
import imaplib
import getpass
import re
import time
import datetime
import pandas as pd

def getChinese(context):
    # context = context.decode("utf-8") # convert context from str to unicode
    filtrate = re.compile(u'[^\u4E00-\u9FA5]') # non-Chinese unicode range
    context = filtrate.sub(r'', context) # remove all non-Chinese characters
    context = context.encode("utf-8") # convert unicode back to str
    return context

es = Elasticsearch() # declare an instance of elasticsearch
server = imaplib.IMAP4_SSL("imap-mail.outlook.com") # access the outlook archive via IMAP protocol
user = input("Username: ")
password = getpass.getpass("Password: ")
server.login(user, password)
server.select("INBOX")
typ, data = server.search(None, "ALL")
counter = 0
file = open("all_emails.txt", "w")
# Iterate through all the emails in the inbox
for num in data[0].split():
    typ, msg_data = server.fetch(num, "(RFC822)")
    raw_email = msg_data[0][1]
    raw_email_string = raw_email.decode("utf-8")
    email_message = email.message_from_string(raw_email_string) # converts email to string
    body = ""
    parsed_date = email.utils.parsedate(email_message.get('date'))
    new_time = time.mktime(parsed_date)
    time_obj = datetime.datetime.fromtimestamp(new_time)
    # code directly below is for limiting the dataset to a certain date
    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(days=7)
    if(time_obj < end_time and time_obj > start_time):
    # parse only the text from the email
        for part in email_message.walk():
            if part.get_content_type() == 'text/html':
                body = part.get_payload(decode=True)
                soup = BeautifulSoup(body, features="html.parser")
                # store in elasticsearch and a text file
                chinese = getChinese(soup.get_text()).decode('utf-8')
                file.write(chinese + "\n")
                es.index(
                        index="comm_platform_via_python",
                        doc_type="emails",
                        id=counter,
                        body={
                            "sender": email_message.get('from'),
                            "recipient": email_message.get('to'),
                            "subject": email_message.get('subject'),
                            "msg_body": soup.get_text(),
                            "cc": email_message.get('cc'),
                            "date": pd.to_datetime(email_message.get('date'))
                        }) # update index with new email
                counter += 1
        # get attachments
        # elif part.get_filename() is not None and 'multipart' not in part.get_content_type():
        #     attachment = open(part.get_filename(), "wb")
        #     attachment.write(part.get_payload(decode=True))
        #     es.index(
        #         index="comm_platform_via_python",
        #         doc_type="emails",
        #         id=counter,
        #         body={"attachment": attachment},
        #     )
        #     counter += 1
        #     attachment.close()
file.close()
server.close()
server.logout()