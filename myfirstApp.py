from flask import Flask, render_template, send_file, redirect, request, url_for, flash,session
from werkzeug.utils import secure_filename
from uuid import uuid4
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import os
from utilities import *
from decorators import isOwner
from flask_s3 import FlaskS3, url_for
##APP SETTINGS
app = Flask(__name__,)
app.secret_key = os.environ["APP_SECRET_KEY"]
app.config['UPLOAD_FOLDER'] = 'static/images/'
app.config['UPLOAD_DOC'] = 'static/docs/'

#MONGODB SETTINGS
app.config["MONGO_URI"] = os.environ['MONGO_URI'].format(os.environ['DB_USERNAME'],os.environ['PASSWORD'], os.environ['DATABASE_NAME'])[1:-1]
mongo = PyMongo(app)
database = mongo.db

#AWS 

app.config["FLASKS3_BUCKET_NAME"] = os.environ["S3_BUCKET_NAME"]
app.config['AWS_ACCESS_KEY_ID'] = os.environ["S3_ACCESS_KEY_ID"]
app.config['AWS_SECRET_ACCESS_KEY'] = os.environ["S3_SECRET_KEY"]
s3 = FlaskS3(app)


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

@app.route("/about")
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
    flash('static/docs/'+filename)
    return send_file(getObject(app, 'static/docs/'+filename)["Body"], mimetype="application/pdf")



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

############ AVAILABLE ONLY IN DEVELOPEMENT
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
   project['no_order'] = int(request.form['no_order'])
   pictures = request.files.getlist('project_pictures')
   for picture in pictures:
       filename = secure_filename(picture.filename)
       project['project_pictures'].append(secure_filename(picture.filename))
       upload_file_to_s3(app,'UPLOAD_FOLDER',picture)
   database.projects.insert_one(project)
   flash('{} has been added at collection'.format(project['project_name']))
   return redirect(url_for('update_view'))

@app.route("/add_course",methods=["POST"])
@isOwner(database)
def add_course():
   newCourse = request.form.to_dict()
   newCourse['class'] = request.form.getlist('class')
   newCourse['no_order'] = int(request.form['no_order'])
   picture = request.files['course_picture']
   diploma = request.files['course_diploma']
   if diploma:
      upload_file_to_s3(app,'UPLOAD_DOC',diploma)
   upload_file_to_s3(app,'UPLOAD_FOLDER',picture)
   newCourse['course_picture'] = secure_filename(picture.filename)
   newCourse['course_diploma'] = secure_filename(diploma.filename)
   database.studies.insert_one(newCourse)
   flash("{} has been added at collection ".format(newCourse['course_name']))
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
       flash('{} has been updated'.format(skill_type['name']))
   else:
       newEntry ={
           "name":newSkill['skill_type'],
           "skills":newSkill['skill']
           }
       database.skills.insert_one(newEntry)
       flash('{} has been added at collection'.format(newEntry['name']))
   return redirect(url_for('update_view'))

@app.route("/add_goal",methods=["POST"])
@isOwner(database)
def add_goal():
   newGoal = request.form.to_dict()
   newGoal['isMain'] = True if 'isMain' in request.form.to_dict().keys() else False
   newGoal['isDone'] = True if 'isDone' in request.form.to_dict().keys() else False
   newGoal['no_order'] = int(newGoal['no_order'])
   database.dreams.insert_one(newGoal)
   flash('{} has been added at collection'.format(newGoal['title']))
   return redirect(url_for('update_view'))

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method =="POST":
        if request.form['password'] == OWNER_PASSWORD:
            user_uuid = str(uuid4())
            database.owner.insert_one({"user_uuid":user_uuid})

            session['user_uuid'] = user_uuid
            flash("Welcome back owner")
            message = "Somebody logged in: " + request.remote_addr
            activity_email(message)
            return redirect((url_for('update_view')))
        else:
            flash("The password is wrong")
            return render_template('login.html', wrong_password=True)

    if database.owner.find_one({"user_uuid":session.get('user_uuid', "xxxxxxxx")}):
        flash("You are already logged in")
        return redirect('update')
    return render_template('login.html', wrong_password=False)

@app.route("/logout", methods=['GET'])
@isOwner(database)
def logout():
    database.owner.delete_many({"user_uuid":session['user_uuid']})
    flash("You has been logged out")
    return redirect(url_for('index'))

@app.route('/list')
@isOwner(database)
def list_assets():
    projects = list(database.projects.find())
    courses = list(database.studies.find())
    skill_sets = list(database.skills.find())
    goals = list(database.dreams.find())
    return render_template('list.html', projects=projects,courses=courses, skill_sets=skill_sets, goals=goals)


@app.route('/delete/<asset>/<asset_id>')
@isOwner(database)
def delete(asset, asset_id):
    if asset=="project":
        proj_pictures = database.projects.find_one({'_id':ObjectId(asset_id)})['project_pictures']
        for pic in proj_pictures:
            delete_file_at_s3(app,pic,"UPLOAD_FOLDER")
        flash("Project has been removed")
        database.projects.delete_one({'_id':ObjectId(asset_id)})
    elif asset =="course":
        course_picture = database.studies.find_one({'_id':ObjectId(asset_id)})['course_picture']
        course_diploma = database.studies.find_one({'_id':ObjectId(asset_id)})['course_diploma']
        delete_file_at_s3(app,course_diploma,'UPLOAD_DOC')
        delete_file_at_s3(app,course_picture,'UPLOAD_FOLDER')
        flash("Course has been removed")
        database.studies.delete_one({'_id':ObjectId(asset_id)})
    elif asset == "skill_set":
        flash("Skill_set has been removed")
        database.skills.delete_one({'_id':ObjectId(asset_id)})
    elif asset =="goal":
        flash("Goal has been removed")
        database.dreams.delete_one({'_id':ObjectId(asset_id)})
    return redirect(url_for('list_assets'))

@app.route('/edit/<asset>/<asset_id>', methods=['GET','POST'])
@isOwner(database)
def edit(asset, asset_id):
    if asset=="project":
        if request.method=="POST":
            newData = request.form.to_dict()
            newData['features'] = request.form.getlist('features')
            newData['technologies'] = request.form.getlist('technologies')
            newData['others_project'] = request.form.getlist('others_project')
            newData['no_order'] = int(newData['no_order'])
            pictures = request.files.getlist('project_pictures')
            newPictures = list()
            deletePic = list()
            currentPictures = database.projects.find_one({'_id':ObjectId(asset_id)})['project_pictures']
            for picture in pictures: # if so add them in the storage
                upload_file_to_s3(app,'UPLOAD_FOLDER',picture)
                newPictures.append(secure_filename(picture.filename))
            if "delete_picture" in newData.keys(): # some of the current pic has been deleted
                deletePic = request.form.getlist('delete_picture')
                for pic in deletePic: # if so remove them from storage
                    delete_file_at_s3(app,pic,"UPLOAD_FOLDER")
                    currentPictures.remove(pic) # remove them from list
                newData.pop('delete_picture')
            newData['project_pictures'] = newPictures + currentPictures # new set of pictures equals the union between new and current pictures left
            database.projects.update_one({"_id":ObjectId(asset_id)},  {"$set":newData})
            flash("Project has been updated")
            return redirect(url_for('project_view', project_id = asset_id ))
        project = database.projects.find_one({'_id':ObjectId(asset_id)})
        return render_template('edit.html', form = "elements/forms/project_form.html" , form_values = project)
    elif asset =="course":
        course = database.studies.find_one({'_id':ObjectId(asset_id)})
        if request.method=="POST":
           newData = request.form.to_dict()
           newData['class'] = request.form.getlist('class')
           newData['no_order'] = int(newData['no_order'])
           picture = request.files['course_picture']
           if picture.filename!="":
               delete_file_at_s3(app,course['course_picture'],'UPLOAD_FOLDER')
               upload_file_to_s3(app,'UPLOAD_FOLDER',picture)
               newData['course_picture'] = secure_filename(picture.filename)
           diploma = request.files['course_diploma']
           if diploma.filename!="":
               delete_file_at_s3(app,course['course_diploma'],'UPLOAD_DOC')
               upload_file_to_s3(app,'UPLOAD_DOC',diploma)
               newData['course_diploma'] = secure_filename(diploma.filename)
           flash("Course has been updated")
           database.studies.update_one({"_id":ObjectId(asset_id)},  {"$set":newData})
           return redirect(url_for('student'))
        return render_template('edit.html', form = 'elements/forms/course_form.html', form_values = course)
    elif asset == "skill_set":
        skill_set = database.skills.find_one({'_id':ObjectId(asset_id)})
        if request.method=="POST":
           newData = request.form.to_dict()
           newData['skills'] = request.form.getlist('skill')
           database.skills.update_one({'_id':ObjectId(asset_id)},{'$set':newData})
           flash("Skill set has been updated")
           return redirect(url_for('developer'))
        return render_template('edit.html', form = 'elements/forms/skill_form.html', form_values = skill_set)
    elif asset =="goal":
        goal = database.dreams.find_one({'_id':ObjectId(asset_id)})
        if request.method=="POST":
           newData = request.form.to_dict()
           newData['isMain'] = True if 'isMain' in request.form.to_dict().keys() else False
           newData['isDone'] = True if 'isDone' in request.form.to_dict().keys() else False
           newData['no_order'] = int(newData['no_order'])
           database.dreams.update_one({'_id':ObjectId(asset_id)},{'$set':newData})
           flash("Goal has been updated")
           return redirect(url_for('dreamer'))
        return render_template('edit.html', form = 'elements/forms/goal_form.html', form_values = goal)
    elif asset =="cv":
        wrong_file_type = False
        if request.method=="POST":
           cv= request.files['cv']
           if cv.filename.endswith('.pdf'):
                currCv = database.cvs.find_one();
                try:
                    os.remove(app.config['UPLOAD_DOC']+"/"+ currCv['filename'])
                except:
                    pass
                cv.save(os.path.join(app.config['UPLOAD_DOC'], secure_filename(cv.filename)))
                database.cvs.update_one({},{"$set":{'filename':secure_filename(cv.filename)}})
                flash("The cv has been updated")
                return redirect(url_for('index'))
           else:
                flash("Wrong file type, the file has to be pdf");
                return redirect(url_for('update_view'))
        return redirect(url_for('update_view'))
    return redirect(url_for('list_assets'))
