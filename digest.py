#!/usr/bin/env python3

import configparser
import datetime
import os
import smtplib
import sys

import lib.hn as hn
import lib.reddit as reddit
import lib.calendarvim as calendarvim

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from tabulate import tabulate

def main():
    config = get_config_options()
    send_digest_email(config)


def send_digest_email(config):
    msg = build_email(config)
    send_email(config, msg)


def build_hn_message():
    posts = hn.get_posts()
    hn_link = 'https://news.ycombinator.com/item?id='
    table_headers = ['Post', 'Link to source', 'Link To Comments']
    table_data = []

    for post in posts:
        table_data.append([
            post['title'],
            post['url'],
            hn_link + str(post['id'])
        ])
    return tabulate(table_data, table_headers, tablefmt='html')


def build_reddit_message(config):
    table_headers = ['Subreddit', 'URL', 'Post URL']
    table_data = []
    r = reddit.Reddit(
        config['Reddit']['cid'],
        config['Reddit']['csecret'],
        config['Reddit']['password'],
        config['Reddit']['useragent'],
        config['Reddit']['username'],
    )
    subreddits = r.get_user_subreddits()
    for subreddit in subreddits:
        posts = r.get_subreddit_hot(subreddit, number_of_posts=3)
        for post in posts:
            table_data.append([
                subreddit.display_name,
                post.url,
                post.shortlink
            ])

    return tabulate(table_data, table_headers, tablefmt='html')


def build_from_events(config):
    calendar = calendarvim.CalendarVim(
        config['Calendar']['calendar_folder']
    )
    today = datetime.date.today()
    forecast_days = config.getint('Calendar', 'forecast_days')
    if forecast_days:
        calendar_events = calendar.get_events_for_day(today,
            forecast=forecast_days)
    else:
        calendar_events = calendar.get_events_for_day(today)

    table_headers = ['Calendar', 'Event', 'Time Start', 'Time End']
    table_data = []

    for calendar in calendar_events:
        if len(calendar_events[calendar]) == 0:
            continue
        for event in calendar_events[calendar]:
            start_time = "{:02d}:{:02d}".format(event.start.hour, event.start.second)
            end_time = "{:02d}:{:02d}".format(event.end.hour, event.end.second)
            table_data.append([
                calendar.summary,
                event.summary,
                start_time,
                end_time
           ])

    return tabulate(table_data, table_headers, tablefmt='html')


def build_email_message(config):
    pass


def build_email(config):
    # NOTE: double up all {  } otherwise you'll get a keyerror from format
    msg = """\
    <html>
        <head>Daily Digest</heady>
        <body>
    <style>
    table, td, th {{
        border: 1px solid black;

    }}

    table {{
        border-collapse: collapse;
            width: 100%;

    }}

    th {{
        height: 50px;

    }}
    </style>
    <br />
    <b>Calendar:</b>
    {calendar}
    <br />
    <b> HN: </b>
    {hn}
    <br />
    <b>Reddit:</b>
    {reddit}

    </body>
</html>
""".format(calendar=build_from_events(config)
           ,hn=build_hn_message(), reddit=build_reddit_message(config))
    return msg


def get_config_options():
    file_dir, _ = os.path.split(os.path.abspath(__file__))
    config_file = file_dir + '/resources/config.config'

    if not os.path.isfile(config_file):
        print('No config file found')
        sys.exit(0)

    config = configparser.ConfigParser(interpolation=None)
    config.read(config_file)

    return config


# I used ses(aws). grabbed the guiddeee from here.
# http://blog.noenieto.com/2012/06/19/using_amazon_ses_with_your_python_applications.html
def send_email(config, message):
    needed_keys = ['smtp_server', 'smtp_username', 'smtp_password',
                   'smtp_port', 'smtp_tls', 'toaddr', 'fromaddr']
    # I, uh, kinda need these
    for key in needed_keys:
        try:
            config.get('Email', key)
        except configparser.NoOptionError:
            print('Config options for email not set: {}'.format(key))
            sys.exit(0)

    smtp_server = smtplib.SMTP(
        host=config.get('Email', 'smtp_server'),
        port=config.get('Email', 'smtp_port'),
        timeout=10
    )

    smtp_server.starttls()
    smtp_server.ehlo()
    smtp_server.login(config.get('Email', 'smtp_username'),
                      config.get('Email', 'smtp_password'))

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Daily Digest for {}".format(datetime.date.today())
    msg['From'] = config.get('Email', 'fromaddr')
    msg['To'] = config.get('Email', 'toaddr')
    msg.attach(MIMEText(message, 'html'))

    smtp_server.sendmail(config.get('Email', 'fromaddr'),
                         config.get('Email', 'toaddr'),
                         msg.as_string())
    smtp_server.quit()


if __name__ == '__main__':
    main()
