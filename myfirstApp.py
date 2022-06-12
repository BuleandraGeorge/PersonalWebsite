from flask import Flask
from flask import render_template, send_from_directory, redirect
from flask.helpers import url_for
from flask_pymongo import PyMongo
import os
app = Flask(__name__)
app.config["MONGO_URI"] = os.environ['MONGO_URI'].format(os.environ['DB_USERNAME'],os.environ['PASSWORD'], os.environ['DATABASE_NAME'])[1:-1]

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
   return render_template("update.html")

@app.route("/add_project",methods=["POST"])
def add_project():
   print("Add Project Working")
   return redirect(url_for('update_view'))

@app.route("/add_course",methods=["POST"])
def add_course():
   print("Add Course Working")
   return redirect(url_for('update_view'))

@app.route("/add_skill",methods=["POST"])
def add_skill():
   print("Add Skill Working")
   return redirect(url_for('update_view'))

@app.route("/add_goal",methods=["POST"])
def add_goal():
   print("Add Goal Working")
   return redirect(url_for('update_view'))
