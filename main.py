#!/bin/python3

"""
JUST MERCY TEXT APP

This application sends and receives texts
from participants to support scheduling for the
Just Mercy project

Ian Richard Ferguson | Stanford University
"""

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from utils.helper import *
from utils.db import ParseSubjects
import pathlib


##########


app = Flask(__name__)
system_path = app.root_path

app.config["UPLOAD_FOLDER"] = "files/uploads"
app.config["SECRET_KEY"] = "jamil4ever"

if not os.path.exists(os.path.join(system_path, app.config["UPLOAD_FOLDER"])):
    pathlib.Path(os.path.join(system_path, app.config["UPLOAD_FOLDER"])).mkdir(
        parents=True, exist_ok=True
    )

auth = HTTPBasicAuth()
very_secret_pw = generate_password_hash("justmercy2022!")

# Build database if it doesn't exist
sql_init()

print("\n== App Running ==\n")

user_data = {
    "Ian": "justmercy2022!",
    "Sydney": "justmercy2022!",
    "Sam": "justmercy2022!",
    "Daniel": "justmercy2022!",
}


@auth.verify_password
def verify(username, password):
    if not (username and password):
        return False
    return user_data.get(username) == password


##########


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

        return redirect(url_for("index"))

    return render_template("texts.html")


######


@app.route("/participant_log", methods=["GET", "POST"])
@auth.login_required
def participant_log():
    df = db_to_dataframe()
    return render_template("logs/stream.html", data=df)


@app.route("/outgoing_texts", methods=["GET", "POST"])
@auth.login_required
def outgoing_texts():
    data = get_texts(sent_by_me=True)
    return render_template("logs/outgoing_texts.html", data=data)


@app.route("/incoming_texts", methods=["GET", "POST"])
@auth.login_required
def incoming_texts():
    data = get_texts(sent_by_me=False)
    return render_template("logs/incoming_texts.html", data=data)


@app.route("/twilio-errors", methods=["GET", "POST"])
@auth.login_required
def twilio_error_log():
    data = get_twilio_errors()
    return render_template("logs/twilio_errors.html", data=data)


######


@app.route("/update", methods=["GET", "POST"])
@auth.login_required
def update():

    if request.method == "POST":
        sub_name = request.form["ignore_name"]
        sub_number = request.form["ignore_number"]

        ignore_participant(full_name=sub_name, contact_number=sub_number)

        return redirect(url_for("index"))

    return render_template("utilities/update.html")


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

        return redirect(url_for("index"))

    return render_template("utilities/add_to_db.html")


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
            return redirect(url_for("index"))

        except Exception as e:
            return render_template("utilities/new_number.html", error=e)

    return render_template("utilities/new_number.html", error=error)


@app.route("/test_twilio", methods=["GET", "POST"])
@auth.login_required
def test_twilio():
    """
    Test connection to Twilio API
    """

    if request.method == "POST":
        textee = request.form["receive"]

        try:
            test_twilio_wrapper(name=textee)
            flash("TEST SUCCESSFUL")

        except Exception as e:
            raise e

        return redirect(url_for("index"))

    return render_template("utilities/test_twilio.html")


@app.route("/nuclear_option", methods=["GET", "POST"])
@auth.login_required
def nuclear_option():

    if request.method == "POST":
        value = request.form["confirm"].strip().upper()

        if value == "YES":
            sql_init(destroy=True)
            flash("DATABASE RESET SUCCESSFULLY")
            return redirect(url_for("index"))

        else:
            flash(f"DATABASE WAS NOT RESET! You entered {value}")
            return redirect(url_for("index"))

    return render_template("utilities/nuclear_option.html")


##########


@app.route("/sms", methods=["GET", "POST"])
def sms():

    from twilio.twiml.messaging_response import MessagingResponse

    response = MessagingResponse()
    response.message("Give us a call at ‪(650) 223-5997‬ if you have any questions!")

    return str(response)


##########


if __name__ == "__main__":
    app.run(debug=True)
