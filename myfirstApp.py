from itertools import product
from flask import Flask, render_template, send_from_directory, redirect, request, url_for, make_response, get_template_attribute, flash
from werkzeug.utils import secure_filename
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import smtplib
from decorators import isOwner
import os
app = Flask(__name__)
app.config["MONGO_URI"] = os.environ['MONGO_URI'].format(os.environ['DB_USERNAME'],os.environ['PASSWORD'], os.environ['DATABASE_NAME'])[1:-1]
app.config['UPLOAD_FOLDER'] = './static/images'
app.config['UPLOAD_DOC'] = './static/docs'
mongo = PyMongo(app)
database = mongo.db
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
OWNER_PASSWORD = '1234'
@app.route("/")
def index():
    return render_template("index.html", projects=list(database.projects.find()), courses=list(database.studies.find()))

@app.route("/student")
def student():
    studies = list(database.studies.find())
    return render_template("student.html",studies=studies);

@app.route("/developer")
def developer():
    projects = list(database.projects.find())
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
        else:
            secondary_goals.append(goal)
    return render_template("dreamer.html", main_goals=main_goals, secondary_goals=secondary_goals);

@app.route("/show/<filetype>/<file_id>")
def view_file(filetype,file_id):
    if (filetype=='cv'):
        filename= database.cvs.find_one_or_404()['filename']
    elif(filetype=="diploma"):
        filename= database.diplomas.find_one_or_404({"_id":ObjectId(file_id)})['filename']
    else:
        return 404
    return send_from_directory(app.config["UPLOAD_DOC"], filename)

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
   picture.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(picture.filename)))
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
   newGoal['isMain'] = True if 'isMain' in request.form.to_dict().keys() else False
   newData['isDone'] = True if 'isDone' in request.form.to_dict().keys() else False
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
           try:     
               os.remove(app.config['UPLOAD_FOLDER']+"/"+pic)
           except:
               pass
        database.projects.delete_one({'_id':ObjectId(asset_id)})
    elif asset =="course":
        course_picture = database.studies.find_one({'_id':ObjectId(asset_id)})['course_picture']
        try:     
            os.remove(app.config['UPLOAD_FOLDER']+"/"+course_picture)
        except:
            pass
        database.studies.delete_one({'_id':ObjectId(asset_id)})
    elif asset == "skill_set":
        database.skills.delete_one({'_id':ObjectId(asset_id)})
    elif asset =="goal":
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
            pictures = request.files.getlist('project_pictures')
            newPictures = list()
            deletePic = list()
            currentPictures = database.projects.find_one({'_id':ObjectId(asset_id)})['project_pictures']
            for picture in pictures: # if so add them in the storage
                try:
                    picture.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(picture.filename)))
                    newPictures.append(secure_filename(picture.filename))
                except:
                    pass
            if "delete_picture" in newData.keys(): # some of the current pic has been deleted
                deletePic = request.form.getlist('delete_picture')
                for pic in deletePic: # if so remove them from storage
                    try:
                        os.remove(app.config['UPLOAD_FOLDER']+"/"+pic)
                    except:
                        pass
                    currentPictures.remove(pic) # remove them from list
                newData.pop('delete_picture')
            newData['project_pictures'] = newPictures + currentPictures # new set of pictures equals the union between new and current pictures left
            database.projects.update_one({"_id":ObjectId(asset_id)},  {"$set":newData})
            return redirect(url_for('project_view', project_id = asset_id ))
        project = database.projects.find_one({'_id':ObjectId(asset_id)})
        return render_template('edit.html', form = "elements/forms/project_form.html" , form_values = project)
    elif asset =="course":
        course = database.studies.find_one({'_id':ObjectId(asset_id)})
        if request.method=="POST":
           newData = request.form.to_dict()
           newData['class'] = request.form.getlist('class')
           picture = request.files['course_picture']
           try:
                picture.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(picture.filename)))
                os.remove(app.config['UPLOAD_FOLDER']+"/"+ course['course_picture'])
                newData['course_picture'] = secure_filename(picture.filename)
           except:
                pass
           database.studies.update_one({"_id":ObjectId(asset_id)},  {"$set":newData})
           return redirect(url_for('student'))
        return render_template('edit.html', form = 'elements/forms/course_form.html', form_values = course)
    elif asset == "skill_set":
        skill_set = database.skills.find_one({'_id':ObjectId(asset_id)})
        if request.method=="POST":
           newData = request.form.to_dict()
           newData['skills'] = request.form.getlist('skill')
           database.skills.update_one({'_id':ObjectId(asset_id)},{'$set':newData})
           return redirect(url_for('developer'))
        return render_template('edit.html', form = 'elements/forms/skill_form.html', form_values = skill_set)
    elif asset =="goal":
        goal = database.dreams.find_one({'_id':ObjectId(asset_id)})
        if request.method=="POST":
           newData = request.form.to_dict()
           newData['isMain'] = True if 'isMain' in request.form.to_dict().keys() else False
           newData['isDone'] = True if 'isDone' in request.form.to_dict().keys() else False
           database.dreams.update_one({'_id':ObjectId(asset_id)},{'$set':newData})
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


@app.route('/send_email', methods=["POST"])
def contact():
    if request.method == "POST":
        email = request.form.get('email')
        message = request.form.get('message')
        if message=="":
            return redirect(url_for('index'))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(os.environ["CONTACT_EMAIL"], os.environ["EMAIL_PASSWORD"])
        message = 'Subject: {}\n\n{}\n\n Email send by {}'.format("Personal Website Contact", message, email)
        server.sendmail(email, "buleandrageorge@gmail.com", message)
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('not_found_404.html'), 404