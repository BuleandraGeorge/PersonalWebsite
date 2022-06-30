from flask import Flask, render_template, send_from_directory, redirect, request, url_for, flash,session
from werkzeug.utils import secure_filename
from uuid import uuid4
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import os
from utilities import activity_email,

##APP SETTINGS
app = Flask(__name__,)
app.secret_key = os.environ["APP_SECRET_KEY"]
app.config['UPLOAD_FOLDER'] = 'static/images/'
app.config['UPLOAD_DOC'] = 'static/docs/'

#MONGODB SETTINGS
app.config["MONGO_URI"] = os.environ['MONGO_URI'].format(os.environ['DB_USERNAME'],os.environ['PASSWORD'], os.environ['DATABASE_NAME'])[1:-1]
mongo = PyMongo(app)
database = mongo.db

OWNER_PASSWORD = os.environ['OWNER_PASSWORD']

@app.route("/")
def index():
    goals = list(database.dreams.find())
    if len(goals)>0:
        main_goals = [goal for goal in goals if goal['isMain'] and not goal['isDone']]
        main_goals.sort(key=lambda goal: goal['no_order'])
    else:
        main_goals=[{'title':"Success is not final; failure is not fatal: it is the courage to continue that counts. - Winston Churchill."}]
    return render_template("index.html", projects=list(database.projects.find()), courses=list(database.studies.find()), main_goal=main_goals[0])

@app.route("/student")
def student():
    studies = list(database.studies.find())
    studies.sort(key=lambda course:course['no_order'])
    return render_template("student.html",studies=studies);

@app.route("/developer")
def developer():
    projects = list(database.projects.find())
    projects.sort(key=lambda project:project['no_order'])
    skills=list(database.skills.find())
    return render_template("developer.html", projects = projects, skill_sets=skills);

@app.route("/dreamer")
def dreamer():
    goals = list(database.dreams.find())
    main_goals = []
    secondary_goals =[]
    for goal in goals:
        if goal['isMain']:
           main_goals.append(goal)
           main_goals.sort(key=lambda goal:goal['no_order'])
        else:
            secondary_goals.append(goal)
            secondary_goals.sort(key=lambda goal:goal['no_order'])
    return render_template("dreamer.html", main_goals=main_goals, secondary_goals=secondary_goals);

@app.route("/show/<filetype>/<file_id>")
def view_file(filetype,file_id):
    if (filetype=='cv'):
        filename= database.cvs.find_one_or_404()['filename']
    elif(filetype=="diploma"):
        filename= database.studies.find_one_or_404({"_id":ObjectId(file_id)})['course_diploma']
    else:
        return 404
    return send_from_directory(path=flask_s3.url_for('static', filename="docs/"+filename))

@app.route("/project/<string:project_id>")
def project_view(project_id):
    project = database.projects.find_one_or_404({"_id": ObjectId(project_id)})
    return render_template("project.html", project = project);

@app.route('/send_email', methods=["POST"])
def contact():
    if request.method == "POST":
        email = request.form.get('email')
        message = request.form.get('message')
        if message=="":
            flash("The email has to have a message")
            return redirect(url_for('index'))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(os.environ["CONTACT_EMAIL"], os.environ["EMAIL_PASSWORD"])
        message = 'Subject: {}\n\n{}\n\n Email send by {}'.format("Personal Website Contact", message, email)
        server.sendmail(email, "buleandrageorge@gmail.com", message)
    flash("The email has been send")
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('not_found_404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('internal_error_500.html'), 500