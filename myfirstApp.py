from itertools import product
from flask import Flask, render_template, send_from_directory, redirect, request, url_for, make_response
from werkzeug.utils import secure_filename
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from decorators import isOwner
import os
app = Flask(__name__)
app.config["MONGO_URI"] = os.environ['MONGO_URI'].format(os.environ['DB_USERNAME'],os.environ['PASSWORD'], os.environ['DATABASE_NAME'])[1:-1]
app.config['UPLOAD_FOLDER'] = './static/images'
mongo = PyMongo(app)
database = mongo.db
OWNER_PASSWORD = '1234'
@app.route("/")
def index():
    return render_template("index.html", projects=database.projects.find())

@app.route("/student")
def student():
    studies = list(database.studies.find())
    return render_template("student.html",studies=studies);

@app.route("/developer")
def developer():
    projects = list(database.projects.find())
    skills=list(database.skills.find())
    return render_template("developer.html", projects = projects, skills=skills);

@app.route("/dreamer")
def dreamer():
    goals = list(database.dreams.find())
    main_goals = []
    secondary_goals =[]
    for goal in goals:
        if goal['isMain']:
           main_goals.append(goal)
        else:
            secondary_goals.append(goal)
    print(main_goals)
    print(secondary_goals)
    return render_template("dreamer.html", main_goals=main_goals, secondary_goals=secondary_goals);

@app.route("/cv")
def view_cv():
    path = "./static/docs/"
    return send_from_directory(path, 'cv_pdf.pdf')

@app.route("/project/<string:project_id>")
def project_view(project_id):
    project = database.projects.find_one_or_404({"_id": ObjectId(project_id)})
    return render_template("project.html", project = project);


@app.route("/update",methods=["GET"])
@isOwner(database)
def update_view():
    return render_template("update.html", skills=list(database.skills.find()))

@app.route("/add_project",methods=["POST"])
@isOwner(database)
def add_project():
   project =request.form.to_dict()
   project['features'] = request.form.getlist('features')
   project['technologies'] = request.form.getlist('technologies')
   project['others_project'] = request.form.getlist('others_project')
   project['project_pictures'] = list()
   pictures = request.files.getlist('project_pictures')
   for picture in pictures:
       filename = secure_filename(picture.filename)
       project['project_pictures'].append(secure_filename(picture.filename))
       picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
   database.projects.insert_one(project)
   return redirect(url_for('update_view'))

@app.route("/add_course",methods=["POST"])
@isOwner(database)
def add_course():
   newCourse = request.form.to_dict()
   newCourse['class'] = request.form.getlist('class')
   picture = request.files['course_picture']
   picture.save(os.path.join(app.config['UPLOAD_FOLDER'], picture.filename))
   newCourse['course_picture'] = secure_filename(picture.filename)
   database.studies.insert_one(newCourse)
   return redirect(url_for('update_view'))

@app.route("/add_skill",methods=["POST"])
@isOwner(database)
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
@isOwner(database)
def add_goal():
   newGoal = request.form.to_dict()
   newGoal['isMain'] = True if request.form['isMain']=="on" else False
   database.dreams.insert_one(newGoal)
   return redirect(url_for('update_view'))

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method =="POST":
        if request.form['password'] == OWNER_PASSWORD:
            database.owner.insert_one({"user_addr":request.remote_addr})
            return redirect((url_for('update_view')))
        else:
            return render_template('login.html', wrong_password=True,)
    if database.owner.find_one({"user_addr":str(request.remote_addr)}):
        return redirect('update')
    return render_template('login.html', wrong_password=False)

@app.route("/logout", methods=['GET'])
@isOwner(database)
def logout():
    database.owner.delete_many({"user_addr":str(request.remote_addr)})
    return redirect('index')

@app.route('/list')
@isOwner(database)
def list():
    return render_template('edit_pages/list.html')

@app.route('/edit_project/<project_id>')
@isOwner(database)
def edit_project(project_id):
    return render_template('edit_pages/project.html')

@app.route('/edit_course/<course_id>')
@isOwner(database)
def edit_course(course_id):
    return render_template('edit_pages/course.html')

@app.route('/edit_skill_set/<skill_set_id>')
@isOwner(database)
def edit_skill_set(skill_set_id):
    return render_template('edit_pages/skill_set.html')

@app.route('/edit_goal/<goal_id>')
@isOwner(database)
def edit_goal(goal_id):
    return render_template('edit_pages/goal.html')
    