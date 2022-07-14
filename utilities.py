import os, smtplib,  boto3

def activity_email(message):
	server = smtplib.SMTP("smtp.gmail.com", 587)
	server.starttls()
	message = 'Subject: {}\n\n{}'.format("Personal Website Activity", message )
	server.login(os.environ["CONTACT_EMAIL"], os.environ["EMAIL_PASSWORD"])
	server.sendmail(os.environ["CONTACT_EMAIL"], "buleandrageorge@gmail.com", message)


def aws(app):
	return boto3.client(
        "s3",
        aws_access_key_id=app.config["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY']
    )

def getObject(app, file_path):
	return aws(app).get_object(Bucket=os.environ["S3_BUCKET_NAME"], Key=file_path)

def upload_file_to_s3(app,bucket_directory,file_object):
    """
    Uploads a file at s3 using:
    app: current application
    bucket_directory: the key of app config dictionary where is the path of the dictionary in the bucket where to be stored
    file_object: file to be uploaded
    """
    try:
      
       aws(app).upload_fileobj(
           file_object,
           app.config['FLASKS3_BUCKET_NAME'],
           app.config[bucket_directory]+file_object.filename,
           ExtraArgs={
                      "ContentType": file_object.content_type
                     }
        )
    except Exception as e:
        return {"success":False, 'message':"The files couldn't be uploaded"}
    return {"success":True, 'message':"The file has been uploaded with success"}

def delete_file_at_s3(app,file_name,bucket_directory):
    """
    Deletes a file at s3 using:
    app: current application
    file_name: file name to be deleted
    bucket_directory: the key of app config dictionary where is the path for the dictionary in the bucket where is stored
    """
    try:
        aws(app).delete_object(
               Bucket=app.config['FLASKS3_BUCKET_NAME'],
               Key=app.config[bucket_directory]+file_name
        )     
    except:
        return (False,"The file couldn't be uploaded")
    return (True,"File uploaded with success") 