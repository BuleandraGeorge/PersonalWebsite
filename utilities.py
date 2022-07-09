import os, smtplib,  boto3

def activity_email(message):
	server = smtplib.SMTP("smtp.gmail.com", 587)
	server.starttls()
	message = 'Subject: {}\n\n{}'.format("Personal Website Activity", message )
	server.login(os.environ["CONTACT_EMAIL"], os.environ["EMAIL_PASSWORD"])
	server.sendmail(os.environ["CONTACT_EMAIL"], "buleandrageorge@gmail.com", message)


def aws(app):
	b3 = boto3.client(
        "s3",
        aws_access_key_id=app.config["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY']
    )
	return b3

def getObject(app, file_path):
	return aws(app).get_object(Bucket=os.environ["S3_BUCKET_NAME"], Key=file_path)