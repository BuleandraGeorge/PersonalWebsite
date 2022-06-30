import smtplib
import os
def activity_email(message):
	server = smtplib.SMTP("smtp.gmail.com", 587)
	server.starttls()
	message = 'Subject: {}\n\n{}'.format("Personal Website Activity", message )
	server.login(os.environ["CONTACT_EMAIL"], os.environ["EMAIL_PASSWORD"])
	server.sendmail(os.environ["CONTACT_EMAIL"], "buleandrageorge@gmail.com", message)