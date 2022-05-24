#!/bin/python3

"""
Helper Functions
"""

# --- Imports
import sqlite3, json, os
from datetime import datetime
import pandas as pd
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from flask import request

# This will change once it's on the server
here = os.path.join(".")

# --- Twilio Helpers
def twilio_init():
    with open(os.path.join(here, "twilio.json")) as incoming:
        creds = json.load(incoming)

    return creds["sid"], creds["auth"], creds["my_number"]


TWIL_account, TWIL_auth, TWIL_number = twilio_init()
API = Client(TWIL_account, TWIL_auth)


def stream_to_dataframe():

    output = pd.DataFrame()

    for text in API.messages.stream():

        if text.from_ != "+18043732715":

            try:
                temp = pd.DataFrame({
                    "created": text.date_sent,
                    "from": text.from_,
                    "text_body": text.body
                }, index=[0])
            
            except:
                continue

            output = output.append(temp, ignore_index=True)

    return output


# --- SQL Helpers
