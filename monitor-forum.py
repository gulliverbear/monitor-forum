#!/usr/bin/env python3

'''
Check phpBB forum for new posts
Sends email notification when new posts found
'''

from bs4 import BeautifulSoup
import requests
import datetime
import time
import smtplib

def send_email(new_posts, gmail_user, gmail_pwd, email_recipients, url, port_number):
    '''
    Send email notification about new posts on forum
    '''
    text = 'Hello!\n'
    text += f'There has been activity on the forums!\n{url}\n'

    for d in new_posts:
        text += '\n'
        text += "Posted by: {}\n".format(d['username'])
        text += "Forum: {}\n".format(d['forum'])
        text += "Topic: {}\n".format(d['topic_text'])
        text += "URL: {}\n".format(d['url'])


    FROM = gmail_user
    TO = email_recipients #must be a list
    SUBJECT = "Activity on the forum"
    TEXT = text

    # Prepare actual message
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", port_number)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print('*** sent email ***')
    except Exception as e:
        print(e)
        print("*** failed to send mail ***")

def convert_dt(s):
    '''
    converts string format to datetime object
    expected format: Thu Mar 14, 2020 9:43 am
    '''
    return datetime.datetime.strptime(s, '%a %b %d, %Y %I:%M %p')

def check_forum(url, last_check, forum, seconds_between_requests):
    '''
    TO DO: Crawl through forum pages looking for any new posts
    '''
    pass

minutes_between_checks = 10
seconds_between_requests = 2
last_check_file = 'last-check.txt'

# user must supply the following:
url = "PUT URL OF FORUM"
gmail_user = "PUT EMAIL ADDRESS OF ACCOUNT SENDING NOTIFICATION"
gmail_pwd = "PUT PASSWORD"
email_recipients = ["EMAIL ADDRESS 1", "EMAIL ADDRESS 2",]
port_number = "PUT GMAIL PORT # HERE"

# read in last_check from file, format should be: Thu Mar 14, 2020 9:43 am
with open(last_check_file) as f:
    last_check = convert_dt(f.read().strip())

# read in main forum page
page = requests.get(url)
soup = BeautifulSoup(page.text, 'html.parser')

# loop through all forums
while True:
    # save the time now so that we can refer back to it for next check
    now_dt = datetime.datetime.now()
    print('checking at {}...'.format(now_dt))
    new_posts = [] # list of dicts
    for forum in soup.find_all('a', class_='forumtitle'):
        time.sleep(seconds_between_requests)
        new_posts += check_forum(url + forum['href'], last_check, forum.text, 
            seconds_between_requests)

    if new_posts:
        send_email(new_posts, gmail_user, gmail_pwd, email_recipients, url, port_number)

    # save the new last_check and write it to file
    last_check = now_dt
    with open(last_check_file, 'w') as fo:
        last_check_string = datetime.datetime.strftime(last_check, 
            '%a %b %d, %Y %I:%M %p')
        fo.write(last_check_string)
    print('sleeping...')
    time.sleep(minutes_between_checks * 60)
