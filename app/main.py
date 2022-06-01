#!/bin/python3

"""
JUST MERCY TEXT APP

This application sends and receives texts
from participants to support scheduling for the
Just Mercy project

Ian Richard Ferguson | Stanford University
"""

# --- Imports
from flask import Flask, render_template, request, redirect, url_for
from helper import *
import os


# --- Initialize application
app = Flask(__name__)
system_path = os.path.join(".")

# Build database if it doesn't exist
sql_init() 

print("\n== App Running ==\n")



# ==== Routing ====
# --- Login
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        if request.form['password'] != "justmercy":
            error = "INVALID PASSWORD"
        else:
            return redirect(url_for("index"))

    return render_template("login.html", error=error)


# --- Index
@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@app.route("/distribute", methods=["GET", "POST"])
def texts():

    if request.method == "POST":

        data = db_to_dataframe()
        send_texts(dataframe=data)

        return redirect(url_for('index'))

    return render_template("texts.html")


# --- Logs
@app.route("/participant_log", methods=["GET", "POST"])
def participant_log():
    data = db_to_dataframe()
    return render_template("stream.html", data=data.to_html())


@app.route("/outgoing_texts", methods=["GET", "POST"])
def outgoing_texts():
    data = get_texts(sent_by_me=True)
    return render_template("outgoing_texts.html", data=data.to_html())


@app.route("/incoming_texts", methods=["GET", "POST"])
def incoming_texts():
    data = get_texts(sent_by_me=False)
    return render_template("incoming_texts.html", data=data.to_html())


# --- Utilities
@app.route("/update", methods=["GET", "POST"])
def update():

    if request.method == "POST":
        sub_name = request.form["ignore_name"]
        sub_number = request.form["ignore_number"]

        ignore_participant(full_name=sub_name,
                           contact_number=sub_number)

        return redirect(url_for('index'))
        
    return render_template("update.html")


@app.route("/add-to-db", methods=["GET", "POST"])
def add_to_db():

    if request.method == "POST":
        name_ = request.form["sub_name"]
        phone = request.form["sub_number"]
        date_ = request.form["sub_date"]

        add_subject_to_db(name=name_,
                          phone_number=phone,
                          study_date=date_)

        return redirect(url_for('index'))

    return render_template("add_to_db.html")


if __name__ == "__main__":
    app.run(debug=True)