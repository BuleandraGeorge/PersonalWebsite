import smtplib
import boto3
import os
def activity_email(message):
	server = smtplib.SMTP("smtp.gmail.com", 587)
	server.starttls()
	message = 'Subject: {}\n\n{}'.format("Personal Website Activity", message )
	server.login(os.environ["CONTACT_EMAIL"], os.environ["EMAIL_PASSWORD"])
	server.sendmail(os.environ["CONTACT_EMAIL"], "buleandrageorge@gmail.com", message)

def upload_file_to_s3(app,bucket_directory,file_object):
    """
    Uploads a file at s3 using:
    app: current application
    bucket_directory: the key of app config dictionary where is the path of the dictionary in the bucket where to be stored
    file_object: file to be uploaded
    """
    b3 = boto3.client(
        "s3",
        aws_access_key_id=app.config["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY']
    )
    try:
        b3.upload_fileobj(
           file_object,
           app.config['FLASKS3_BUCKET_NAME'],
           app.config[bucket_directory]+file_object.filename,
           ExtraArgs={
                      "ContentType": file_object.content_type
                     }
        )
    except:
        return {"success":False, 'message':"The files couldn't be uploaded"}
    return {"success":True, 'message':"The file has been uploaded with success"}

def delete_file_at_s3(app,file_name,bucket_directory):
    """
    Deletes a file at s3 using:
    app: current application
    file_name: file name to be deleted
    bucket_directory: the key of app config dictionary where is the path for the dictionary in the bucket where is stored
    """
    b3 = boto3.client(
         "s3",
         aws_access_key_id=app.config["AWS_ACCESS_KEY_ID"],
         aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY']
    )
    try:
        b3.delete_object(
               Bucket=app.config['FLASKS3_BUCKET_NAME'],
               Key=app.config[bucket_directory]+file_name
        )     
    except:
        return (False,"The file couldn't be uploaded")
    return (True,"File uploaded with success")