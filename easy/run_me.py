#!/bin/python3

"""
About this Script

This is an automated setup to text
participants in the Just Mercy project

Ian Richard Ferguson
"""

# --- Imports
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import os, json
from twilio.rest import Client
from datetime import datetime

here = os.path.join(".")


# --- Helpers
def twilio_init():
    with open(os.path.join(here, "twilio.json")) as incoming:
        creds = json.load(incoming)

    return creds["sid"], creds["auth"], creds["my_number"]


def message_tree(iteration, first_name):

    if iteration == 1:
        message = f"""Hi {first_name.title()}!\n
This is Sydney from the Narratives Project. We would like to invite you to participate in the study. We emailed you more information. \n
If you did not receive the email or you are no longer interested in participating, please give us a call at ‪(650) 223-5997‬. Thank you!
        """

    elif iteration == 2:
        message = f"""Hi {first_name.title()}!\n
This is Sydney from the Narratives Project. This is what participants will see on their SECOND contact iteration.\n
Hope this worked!
        """

    elif iteration == 3:
        message = f"""Hi {first_name.title()}!\n
This is Sydney from the Narratives Project. This is what participants will see on their SECOND contact iteration.\n
So far so good!
        """

    return message


def main():

    subs = pd.read_csv(os.path.join(here, "participants.csv"), sep="\t")
    subs.fillna("INCOMPLETE", inplace=True)

    today = datetime.today().strftime("%m/%d/%Y")

    SID, AUTH, MY_NUMBER = twilio_init()
    API = Client(SID, AUTH)

    for ix, name in enumerate(subs['name']):

        contact_number = subs['number'][ix]

        first_name = name.split(' ')[0].title()

        if subs['first_contact'][ix] == "INCOMPLETE":
            iter = 1
        elif subs['second_contact'][ix] == "INCOMPLETE":
            iter = 2
        elif subs['third_contact'][ix] == "INCOMPLETE":
            iter = 3

        message = message_tree(iteration=iter, first_name=first_name)

        API.messages.create(to=contact_number,
                            from_=MY_NUMBER,
                            body=message)


        if iter == 1:
            subs['first_contact'][ix] = today
        elif iter == 2:
            subs['second_contact'][ix] = today
        elif iter == 3:
            subs['third_contact'][ix] = today

    subs.to_csv(os.path.join(here, "participants.csv"), index=False, sep="\t")
    print("\n== All participants contacted ==\n")


if __name__ == "__main__":
    main()