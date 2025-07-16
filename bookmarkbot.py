#!/usr/bin/env python
# -*- coding: utf-8 -*-
import email
from email.header import decode_header
import imaplib
import logging
import pinboard
import re
import time

from unipath import Path

PROJECT_DIR = Path(__file__).ancestor(1)
LOG_DIR = PROJECT_DIR.child('log')


daily_log = str(LOG_DIR.child('log-' + str(time.strftime("%m-%d-%y")) + '.log'))
logging.basicConfig(
    format='%(asctime)s (%(levelname)s) - %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    filename=daily_log, level=logging.DEBUG)

# set up logging
logging.info('Starting logger for Bookmarkbot')


def run_bookmarkbot(_imap_server, _email_username, _email_password, _pinboard_username, _pinboard_password):
    logging.info(f'_imap_server={_imap_server}, _email_username={_email_username}')
    logging.info(f'_pinboard_username={_pinboard_username}')
    mail_box = imaplib.IMAP4_SSL(_imap_server)

    try:
        mail_box.login(_email_username, _email_password)

    except imaplib.IMAP4.error:
        logging.error("LOGIN FAILED!!!")
        # ... exit or deal with failure...
        exit()

#    rv, mailboxes = mail_box.list()
#    if rv == 'OK':
#        logging.info("Mailboxes:")
#        logging.info(mailboxes)

    rv, data = mail_box.select("INBOX")
    if rv == 'OK':
        logging.info("Processing mailbox...\n")
        process_mailbox(mail_box, _pinboard_username, _pinboard_password)  # ... do something with emails, see below ...
        mail_box.close()
        mail_box.logout()


def process_mailbox(mailbox, _pinboard_username, _pinboard_password):
    # find all 'unseen' messages
    rv, data = mailbox.search(None, 'UnSeen')

    if rv == 'OK':
        pinboard_conn = pinboard.open(_pinboard_username, _pinboard_password)

        for num in data[0].split():
            rv2, data2 = mailbox.fetch(num, '(RFC822)')
            if rv2 != 'OK':
                logging.error("ERROR getting message {0}".format(num))
                return

            msg = email.message_from_bytes(data2[0][1])

            dh = decode_header(msg.get('subject'))

            default_charset = 'ASCII'

            subject = ''.join([str(t[0], t[1] or default_charset) if isinstance(t[0], bytes) else t[0] for t in dh])

            charmap = {
                0x201c: u'"',
                0x201d: u'"',
                0x2018: u"'",
                0x2019: u"'",
                0x2014: u'-',
            }

            subject = subject.translate(charmap)
            subject = subject.replace('[peterl]', '').replace('\n', ' ').replace('\r', '')
            subject = subject.strip()

            logging.info(u'Message {0}: {1}'.format(num, subject))
            logging.info(u'Raw Date: {0}'.format(msg['Date']))

            body = get_first_text_block(msg)
            urls = re.findall(
                r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                body)

            logging.info(u'URL: {0}'.format(urls[0]))
            pinboard_conn.add(urls[0], subject)

            # mark as seen
            # mailbox.store(data[0].replace(' ', ','), '+FLAGS', '\Seen')
#            mailbox.store(data[0].replace(' ', ','), '+FLAGS', '\UnSeen')
        else:
            logging.info(u'rv: {0}'.format(rv))

    return


def get_first_text_block(msg):

    payloads = []

    for part in msg.walk():
        if part.get_content_maintype() == "multipart":
            continue
        payloads.append(part.get_payload(decode=1))

    return payloads[0]


if __name__ == "__main__":
    import configparser

    config = configparser.ConfigParser()
    config.read("bookmarkbot.ini")

    dConfig = config.__dict__['_sections'].copy()

    imap_server = dConfig['email']['imap_server']
    email_username = dConfig['email']['username']
    email_password = dConfig['email']['password']
    pinboard_username = dConfig['pinboard']['username']
    pinboard_password = dConfig['pinboard']['password']

    run_bookmarkbot(imap_server, email_username, email_password, pinboard_username, pinboard_password)
