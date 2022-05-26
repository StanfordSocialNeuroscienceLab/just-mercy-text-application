#!/bin/python3

"""
Helper Functions
"""

# --- Imports
import sqlite3, json, os
from datetime import datetime
import pandas as pd
from twilio.rest import Client

# This will change once it's on the server
here = os.path.join(".")

# --- Twilio Helpers
def twilio_init():
    """
    This function reads in stored Twilio information and returns
    login credentials to instantiate API connection
    """

    with open(os.path.join(here, "twilio.json")) as incoming:
        creds = json.load(incoming)

    return creds["sid"], creds["auth"], creds["my_number"]


# -- Twilio information + API connection
TWIL_account, TWIL_auth, TWIL_number = twilio_init()
API = Client(TWIL_account, TWIL_auth)


def send_texts(dataframe):
    """
    This function loops through subjects in a dataframe and
    contacts them via SMS text unless they are marked "ignore"

    Parameters
        dataframe: Pandas DataFrame
    """

    # Current date, e.g., 5/26/2022
    today = datetime.today().strftime("%m/%d/%Y")

    # Loop through rows in the dataframe
    for ix, name in enumerate(dataframe['name']):

        # Skip over subjects marked ignore
        if dataframe['ignore'][ix] != "False":
            continue

        # Participant contact number and study date
        contact_number = dataframe['phone_number'][ix]
        study_date = dataframe['date_of_study'][ix]

        # E.g., Ian Ferguson => Ian
        first_name = name.split(' ')[0].title()

        # Determine contact iteration for the given subject
        if dataframe['first_contact'][ix] == "INCOMPLETE":
            iter=1
        elif dataframe['second_contact'][ix] == "INCOMPLETE":
            iter=2
        elif dataframe['third_contact'][ix] == "INCOMPLETE":
            iter=3

        # Text message body derived from helper function
        message = message_tree(iteration=iter, 
                               first_name=first_name, 
                               study_date=study_date)

        # Send text message
        API.messages.create(to=contact_number,
                            from_=TWIL_number,
                            body=message)

        # Update subject's information on database
        update_contact_date(iteration=iter, 
                            full_name=name, 
                            contact_number=contact_number,
                            new_date=today)



def message_tree(iteration, first_name, study_date):
    """
    This function determines what message a subject will receive
    based on how many times they've been contacted previously

    Parameters
        iteration:  int or str | Current iteration of SMS contact with subject
        first_name: str | Subject's first name (e.g., "Ian")
        study_date: str | Date that subject will engage with our research

    Returns
        Long-form string to use as body of SMS text message
    """

    # -- Initial message
    if iteration == 1:
        message = f"""Hi {first_name.title()}!\n
This is Sydney from the Narratives Project. We would like to invite you to participate in the study. We emailed you more information. \n
If you did not receive the email or you are no longer interested in participating, please give us a call at ‪(650) 223-5997‬. Thank you!
            """

    # -- Subsequent messages
    else:
        message = f"""Hi {first_name.title()}!\n
This is Sydney from the Narratives Project. This is a reminder that you're scheduled to participate in our study on {study_date}. \n
If you are no longer interested in participating, please give us a call at ‪(650) 223-5997‬. Thank you!
            """

    return message



# --- SQL Helpers
def sql_init(destroy=False):
    """
    This function ensures that our local SQL database exists, and it
    creates the participants table if it doesn't already exist

    Parameters
        destroy:  Boolean | if True, removes database and recreates it
    """

    # -- Case: Database does not exist
    if not os.path.exists(os.path.join(here, "jm.db")):
        print("\n** Establishing Database **\n")
        
        
        with sqlite3.connect(os.path.join(here, "jm.db")) as connection:
            with open(os.path.join(here, "schema.sql")) as script:
                cursor = connection.cursor()

                print("\n** Creating participants table **\n")
                cursor.executescript(script.read())


    # -- Case: Database exists and we want to start over
    if destroy:
        with sqlite3.connect(os.path.join(here, "jm.db")) as connection:
            with open(os.path.join(here, "schema.sql")) as script:
                cursor = connection.cursor()

                print("\n** Creating participants table **\n")
                cursor.executescript(script.read())



def add_subject_to_db(name, phone_number, study_date):
    """
    This function takes HTML input and pushes information to local SQLite database

    Parameters
        name: str | Subject's full name
        phone_number: str | Subject's contact number
        study_date: str | Date that subject will engage with our research
    """
    
    with sqlite3.connect(os.path.join(here, "jm.db")) as connection:
        cursor = connection.cursor()

        cursor.execute(f"""
        INSERT INTO participants (name,phone_number,date_of_study)
        VALUES (?,?,?)
        """, (name, phone_number, study_date))



def ignore_participant(full_name, contact_number):
    """
    This function updates subject's row in DB so that they are not sent any additional texts

    Parameters
        full_name: str | Subject's full name
        contact_number: str | Subject's contact number
    """

    with sqlite3.connect(os.path.join(here, "jm.db")) as connection:
        cursor = connection.cursor()

        cursor.execute("""
        UPDATE participants
        SET ignore = True
        WHERE name = (?) AND phone_number = (?)
        """, (full_name, contact_number))



def db_to_dataframe():
    """
    This function pulls down all information from our participants table
    and converts it to a Pandas DataFrame
    """
    
    with sqlite3.connect(os.path.join(here, "jm.db")) as connection:
        return pd.read_sql("SELECT * FROM participants", connection)


def get_texts(sent_by_me=False):
    """
    This function aggregates all sent or received texts, based on Boolean parameter
    """

    # -- Empty DF to append into
    output = pd.DataFrame()


    # -- All texts sent to subjects
    if sent_by_me:

        for text in API.messages.stream(from_=TWIL_number):
            temp = pd.DataFrame({
                "date": text.date_created,
                "sent_to": text.to,
                "body": text.body
            }, index=[0])

            output = output.append(temp, ignore_index=True)


    # -- All texts sent to this number
    else:

        for text in API.messages.stream(to=TWIL_number):
            temp = pd.DataFrame({
                "date": text.date_created,
                "sent_from": text.from_,
                "body": text.body
            }, index=[0])

            output = output.append(temp, ignore_index=True)

    if len(output) == 0:
        return pd.DataFrame(columns=['date', 'sent_from', 'body'])

    return output.reset_index(drop=True)


def update_contact_date(iteration, full_name, contact_number, new_date):
    """
    This function updates the contact information in our participants table
    which informs the messaging that subjects will receive in future texts

    Parameters
        iteration: str or int | Iteration of subject contact (1,2,3)
        full_name: str | Subject's full name
        contact_number: str | Subject's phone number
        new_date: str | Today's date, in practice
    """
    
    with sqlite3.connect(os.path.join(here, "jm.db")) as connection:
        cursor = connection.cursor()

        if iteration == 1:
            cursor.execute("""
            UPDATE participants
            SET first_contact = (?)
            WHERE name = (?) AND phone_number = (?)
            """, (new_date, full_name, contact_number))
        
        elif iteration == 2:
            cursor.execute("""
            UPDATE participants
            SET second_contact = (?)
            WHERE name = (?) AND phone_number = (?)
            """, (new_date, full_name, contact_number))
        
        elif iteration == 3:
            cursor.execute(f"""
            UPDATE participants
            SET third_contact = (?)
            WHERE name = (?) AND phone_number = (?)
            """, (new_date, full_name, contact_number))