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



# --- Routing
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


@app.route("/stream", methods=["GET", "POST"])
def stream():
    data = db_to_dataframe()

    return render_template("stream.html", data=data.to_html())


@app.route("/update", methods=["GET", "POST"])
def update():
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