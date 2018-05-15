#! /usr/bin/python

import smtplib
import socket
from  datetime import datetime

class mailMe:

	def __init__(self, mailMe_info):

		self.user = mailMe_info['user']
		self.pwd = mailMe_info['pwd']
		
		self.mailMe_info = mailMe_info

	def __prepare_and_send(self, recipient, subject, body):
		
		FROM = self.user
		TO = recipient if type(recipient) is list else [recipient]
		SUBJECT = subject
		TEXT = body

		# Prepare actual message
		message = """From: %s\nTo: %s\nSubject: %s\n\n%s \n\n\n Time: %s
		""" % (FROM, ", ".join(TO), SUBJECT, TEXT, str(datetime.now()))
		
		try:
			server = smtplib.SMTP("smtp.gmail.com", 587)
			server.ehlo()
			server.starttls()
			server.login(self.user, self.pwd)
			socket.setdefaulttimeout(10)
			server.sendmail(FROM, TO, message)
			server.close()
			print 'successfully sent the mail'
		except:
			print "failed to send mail"



		
	def send_email(self, recipient='', subject='', body=''):

		if self.mailMe_info is not None:
			if recipient == '':
				recipient = self.mailMe_info["recipient"]
			if subject == '':
				subject = self.mailMe_info["default_subject"]
			if body == '':
				body = self.mailMe_info["default_body"]

		self.__prepare_and_send(recipient, subject, body)


	def send_email_warning(self, recipient='', subject='', body=''):

		if self.mailMe_info is not None:
			if recipient == '':
				recipient = self.mailMe_info["recipient"]
			if subject == '':
				subject = self.mailMe_info["default_subject_warning"]
			if body == '':
				body = self.mailMe_info["default_body_warning"]

		self.__prepare_and_send(recipient, subject, body)