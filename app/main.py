#!/bin/python3

"""
JUST MERCY TEXT APP

This application sends and receives texts
from participants to support scheduling for the
Just Mercy project

Ian Richard Ferguson | Stanford University
"""

# --- Imports
from flask import Flask, make_response, render_template, request, redirect, url_for
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from utils.helper import *
from utils.db import ParseSubjects
from functools import wraps
import pathlib


# --- Initialize application
app = Flask(__name__)
system_path = app.root_path

app.config["UPLOAD_FOLDER"] = "files/uploads"

if not os.path.exists(os.path.join(system_path, app.config["UPLOAD_FOLDER"])):
    pathlib.Path(os.path.join(system_path, app.config["UPLOAD_FOLDER"])).mkdir(parents=True, 
                                                                               exist_ok=True)

auth = HTTPBasicAuth()
very_secret_pw = generate_password_hash("justmercy2022!")

# Build database if it doesn't exist
sql_init() 

print("\n== App Running ==\n")

user_data = {
    "Ian": "justmercy2022!",
    "Sydney": "justmercy2022!",
    "Sam": "justmercy2022!",
    "Daniel": "justmercy2022!"
}


@auth.verify_password
def verify(username, password):
    if not (username and password):
        return False
    return user_data.get(username) == password

    

# ==== Routing ====
# --- Login
@app.route("/", methods=["GET", "POST"])
def login():

    error = None

    if request.method == "POST":
        username = request.form["username"].title()
        pw = request.form["password"]

        print("\n\nUsername: {}\nPassword: {}\n\n".format(username, pw))

        if verify(username=username, password=pw):
            return render_template("index.html")

        else:
            error = "Invalid Username or Password"
            return render_template("login.html", error=error)

    return render_template("login.html", error=error)



# --- Index
@app.route("/home", methods=["GET", "POST"])
@auth.login_required
def index():
    return render_template("index.html")



@app.route("/distribute", methods=["GET", "POST"])
@auth.login_required
def texts():

    if request.method == "POST":

        data = db_to_dataframe()
        send_texts(dataframe=data)

        return redirect(url_for('index'))

    return render_template("texts.html")



# --- Logs
@app.route("/participant_log", methods=["GET", "POST"])
@auth.login_required
def participant_log():
    data = db_to_dataframe()
    return render_template("stream.html", data=data.to_html())



@app.route("/outgoing_texts", methods=["GET", "POST"])
@auth.login_required
def outgoing_texts():
    data = get_texts(sent_by_me=True)
    return render_template("outgoing_texts.html", data=data.to_html())



@app.route("/incoming_texts", methods=["GET", "POST"])
@auth.login_required
def incoming_texts():
    data = get_texts(sent_by_me=False)
    return render_template("incoming_texts.html", data=data.to_html())



@app.route("/twilio-errors", methods=["GET", "POST"])
@auth.login_required
def twilio_error_log():
    data = get_twilio_errors()
    return render_template("twilio_errors.html", data=data.to_html())



# --- Utilities
@app.route("/update", methods=["GET", "POST"])
@auth.login_required
def update():

    if request.method == "POST":
        sub_name = request.form["ignore_name"]
        sub_number = request.form["ignore_number"]

        ignore_participant(full_name=sub_name,
                           contact_number=sub_number)

        return redirect(url_for('index'))
        
    return render_template("update.html")



@app.route("/add-to-db", methods=["GET", "POST"])
@auth.login_required
def add_to_db():

    if request.method == "POST":
        
        file = request.files["file"]
        safe_name = secure_filename(file.filename)

        file_path = os.path.join(system_path, app.config["UPLOAD_FOLDER"], safe_name)
        file.save(file_path)

        # -- Push subjects to database
        # Instantiate ParseSubjects object
        pusher = ParseSubjects(app_path=system_path, file=file_path)

        # Push to database
        pusher.run()

        # Remove file
        os.remove(file_path)

        return redirect(url_for('index'))

    return render_template("add_to_db.html")



@app.route("/change_phone_number", methods=["GET", "POST"])
@auth.login_required
def change_phone_number():

    error = None

    if request.method == "POST":

        name = request.form["name"]
        old_n = request.form["old_number"]
        new_n = request.form["new_number"]

        try:
            update_contact_number(name=name, old_number=old_n, new_number=new_n)
            return redirect(url_for('index'))

        except Exception as e:
            return render_template('new_number.html', error=e)

    return render_template('new_number.html', error=error)



@app.route("/sms", methods=["GET", "POST"])
def sms():

    from twilio.twiml.messaging_response import MessagingResponse

    response = MessagingResponse()
    response.message("Give us a call at ???(650) 223-5997??? if you have any questions!")

    return str(response)



if __name__ == "__main__":
    app.run(debug=True)
