from flask import Flask
from flask import render_template
from flask_pymongo import PyMongo
app = Flask(__name__)
"""
app.config["MONGO_URI"] = "mongodb+srv://george:tKlOrnl7yoyzwkQw@all.nmpma.mongodb.net/?retryWrites=true&w=majority"
app.config["MONGO_DBNAME"] = 'personal_details'
mongo = PyMongo(app)
"""
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/student")
def student():
    return render_template("student.html");

@app.route("/developer")
def developer():
    return render_template("developer.html");

@app.route("/dreamer")
def dreamer():
    return render_template("dreamer.html");