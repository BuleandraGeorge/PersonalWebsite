from itertools import product
from flask import Flask, render_template, send_from_directory, redirect, request, url_for
from werkzeug.utils import secure_filename
from flask_pymongo import PyMongo
import os
app = Flask(__name__)
app.config["MONGO_URI"] = os.environ['MONGO_URI'].format(os.environ['DB_USERNAME'],os.environ['PASSWORD'], os.environ['DATABASE_NAME'])[1:-1]
app.config['UPLOAD_FOLDER'] = './static/images'
mongo = PyMongo(app)
database = mongo.db
@app.route("/")
def index():
    return render_template("index.html", projects=database.projects.find())

@app.route("/student")
def student():
    return render_template("student.html");

@app.route("/developer")
def developer():
    return render_template("developer.html");

@app.route("/dreamer")
def dreamer():
    return render_template("dreamer.html");

@app.route("/cv")
def view_cv():
    path = "./static/docs/"
    return send_from_directory(path, 'cv_pdf.pdf')

@app.route("/project")
def project_view():
    return render_template("project.html");


@app.route("/update",methods=["GET"])
def update_view():
   
   return render_template("update.html", skills=list(database.skills.find()))

@app.route("/add_project",methods=["POST"])
def add_project():
   project =request.form.to_dict()
   project['features'] = request.form.getlist('features')
   project['technologies'] = request.form.getlist('technologies')
   project['others-project'] = request.form.getlist('others-project')
   project['project_pictures'] = list()
   pictures = request.files.getlist('project_pictures')
   for picture in pictures:
       filename = secure_filename(picture.filename)
       project['project_pictures'].append(filename)
       picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
   database.projects.insert_one(project)
   return redirect(url_for('update_view'))

@app.route("/add_course",methods=["POST"])
def add_course():
   newCourse = request.form.to_dict()
   newCourse['class'] = request.form.getlist('class')
   picture = request.files['course_picture']
   picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
   newCourse['course_picture'] = secure_filename(picture.filename)
   database.studies.insert_one(newCourse)
   return redirect(url_for('update_view'))

@app.route("/add_skill",methods=["POST"])
def add_skill():
   newSkill = request.form.to_dict()
   newSkill['skill'] = request.form.getlist('skill')
   skill_type = database.skills.find_one({'name':newSkill['skill_type']})
   if skill_type:
       skills = skill_type['skills']
       skills = skills + newSkill['skill']
       myquery = {"skills": skill_type['skills']}
       newvalues = { "$set":{'skills':skills} }
       database.skills.update_one(myquery, newvalues )
   else:
       newEntry ={
           "name":newSkill['skill_type'],
           "skills":newSkill['skill']
           }
       database.skills.insert_one(newEntry)
   return redirect(url_for('update_view'))

@app.route("/add_goal",methods=["POST"])
def add_goal():
   newGoal = request.form.to_dict()
   newGoal['isMain'] = True if request.form['isMain']=="on" else False
   database.dreams.insert_one(newGoal)
   return redirect(url_for('update_view'))
