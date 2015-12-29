#!/usr/bin/env python

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EmailNotification():
    username = "morienstudio@gmail.com"
    password = "qweEWQ123#@!"

    def send(self, email, text, html):
        me = "morienstudio@gmail.com"

        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Zdielanie timelinu v systeme KillDarius"
        msg['From'] = me
        msg['To'] = email

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)

        # Send the message via local SMTP server.
        s = smtplib.SMTP('smtp.gmail.com:587')
        s.starttls()

        s.login(self.username, self.password)
        # sendmail function takes 3 arguments: sender's address, recipient's address
        # and message to send - here it is sent as one string.
        s.sendmail(me, email, msg.as_string())
        s.quit()