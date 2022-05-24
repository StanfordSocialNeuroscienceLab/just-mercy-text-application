#!/bin/python3

"""
JUST MERCY TEXT APP

This application sends and receives texts
from participants to support scheduling for the
Just Merc project

Ian Richard Ferguson | Stanford University
"""

# --- Imports
from flask import Flask, render_template, request, redirect, url_for
from helper import *
import os


# --- App init + routing
app = Flask(__name__)
system_path = os.path.join(".")

print("\n== App Running ==\n")


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@app.route("/distriute", methods=["GET", "POST"])
def texts():
    return render_template("texts.html")


@app.route("/stream", methods=["GET", "POST"])
def stream():

    data = pd.read_csv("./participants.csv", sep="\t")

    return render_template("stream.html", data=data.to_html())


if __name__ == "__main__":
    app.run(debug=True)