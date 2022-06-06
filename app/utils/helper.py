#!/bin/python3

"""
Helper Functions
"""

# --- Imports
import sqlite3, json, os, pytz
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

    with open(os.path.join(here, "packets/twilio.json")) as incoming:
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

        # Text message body derived from helper function
        variable, message = message_tree(study_date=study_date, 
                                         first_name=first_name)

        if message is not None:
            # Send text message
            API.messages.create(to=contact_number,
                                from_=TWIL_number,
                                body=message)

            # Update subject's information on database
            update_contact_date(variable_name=variable,
                                full_name=name, 
                                contact_number=contact_number,
                                new_date=today)



def message_tree(study_date, first_name):
    """
    This function determines what message a subject will receive
    based on how many times they've been contacted previously

    Parameters
        first_name: str | Subject's first name (e.g., "Ian")
        study_date: str | Date that subject will engage with our research

    Returns
        Long-form string to use as body of SMS text message
    """

    today = datetime.now(pytz.timezone("US/Pacific")).strftime("%m/%d/%Y")
    time_delta = get_time_delta(study_date=study_date, check_date=today, method="days")

    # -- Intro text
    if time_delta == -3:
        var = "intro_text"

        message = f"""Hi {first_name}!\n
You have been selected to participate in the Narratives Project! If you are still interested in participating, please read the email we sent you. It might be in your spam folder.\n 
If you have any questions, call or text us at (650)-223-5997 and we will get back to you as soon as possible.
        """
    
    # -- Reminder Day 1
    elif time_delta == 0:
        var = "rem1"

        message = """Hello!\n
Hello! This is your reminder that if you would like to participate in the Narratives Project, please click the link we sent to your email and begin the study. Please complete Visits 1 and 2 by Sunday at 11:59pm.\n 
If you have any questions call or text us at ‪(650) 223-5997‬ and we will get back to you ASAP."""

    # -- Reminder Day 2
    elif time_delta == 2:
        var = "rem2"

        message = """Hello!\n 
This is your reminder that today is the last day to complete Visits 1 and 2 of the Narratives Project. Please click the link we sent to your email and begin (or log back in to finish).
        """

    # -- Reminder Day 3
    elif time_delta == 6:
        var = "rem3"

        message = """Hello!\n
This is your reminder to log back into the website and complete Visit 3 of the Narratives Project. We emailed you the link to log back into the website. Please complete Visit 3 on the day that is 1 week after you completed Visit 2. If you forgot when you completed Visit 2, you can log in to the website and it tells you what day to log back in for Visit 3. \n
And remember: if you complete all 5 visits you will be entered into a raffle to receive an extra $250 giftcard!        
        """

    # -- Reminder Day 4
    elif time_delta == 9:
        var = "rem4"

        message = """Hello!\n 
This is your reminder to log back into the website and complete Visit 3 of the Narratives Project if you have not already done so. We emailed you the link to log back into the website.\n 
And remember: if you complete all 5 visits you will be entered into a raffle to receive an extra $250 giftcard!
        """

    # -- Payment Day 1
    elif time_delta == 11:
        var = "pay1"

        message = """Hello and thank you for participating in part or all of Visits 1-3.\n 
We emailed you your giftcard. Visit 4 will happen in a few weeks - we will email and text you to remind you to complete it.\n 
And remember: if you complete all 5 visits you will be entered into a raffle to receive an extra $250 giftcard! Thanks again!        
        """

    # -- Reminder Day 5
    elif time_delta == 29:
        var = "rem5"

        message = """Hello!\n
This is your reminder to complete Visit 4 of the Narratives Project. Please complete it on the day that is 1 month after you completed Visit 2. If you forgot when you completed Visit 2, you can log in to the website and it tells you what day to log back in for Visit 4.\n 
And remember: if you complete all 5 visits you will be entered into a raffle to receive an extra $250 giftcard!
        """

    # -- Reminder Day 6
    elif time_delta == 32:
        var = "rem6"

        message = """Hello!\n 
This is your reminder to log back into the website and complete Visit 4 of the Narratives Project if you have not already done so. We emailed you the link to log back into the website.\n 
And remember: if you complete all 5 visits you will be entered into a raffle to receive an extra $250 giftcard!
        """

    # -- Payment Day 2
    elif time_delta == 34:
        var = "pay2"

        message = """Hello and thank you for participating in part or all of Visit 4.\n
We emailed you your giftcard. Visit 5 will happen in a few months - we will email and text you to remind you to complete it.\n 
And remember: if you complete all 5 visits you will be entered into a raffle to receive an extra $250 giftcard!
        """

    # -- Reminder Day 7
    elif time_delta == 89:
        var = "rem7"

        message = """Hello!\n 
This is your reminder to complete Visit 5 of the Narratives Project.  Please complete it on the day that is 3 months after you completed Visit 2. If you forgot when you completed Visit 2, you can log in to the website and it tells you what day to log back in for Visit 5.\n 
And remember: if you complete all 5 visits you will be entered into a raffle to receive an extra $250 giftcard!
        """

    # -- Reminder Day 8
    elif time_delta == 92:
        var = "rem8"

        message = """Hello!\n 
This is your reminder to log back into the website and complete Visit 5 of the Narratives Project if you have not already done so. We emailed you the link to log back into the website.\n 
And remember: if you complete all 5 visits you will be entered into a raffle to receive an extra $250 giftcard!        
        """

    # -- Payment Day 3
    elif time_delta == 94:
        var = "pay3"

        message = """
Hello and thank you for participating in part or all of Visit 5. We emailed you your giftcard. Thanks again for participating in the Narratives Project!
        """

    # -- No need to text!
    else:
        return None, None

    return var, message



def get_time_delta(study_date, check_date, method="days"):
    """
    Easy function to calculate distance between check_date (today) and the
    date that the subject engages in our research
    """

    study = datetime.strptime(study_date, "%m/%d/%Y")
    check = datetime.strptime(check_date, "%m/%d/%Y")

    if method == "days":
        return (check - study).days



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
        SET ignore = (?)
        WHERE name = (?) AND phone_number = (?)
        """, (True, full_name, contact_number))



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



def update_contact_date(variable_name, full_name, contact_number, new_date):
    """
    This function updates the contact information in our participants table
    which informs the messaging that subjects will receive in future texts

    Parameters
        variable_name: str | Column name in SQL database
        full_name: str | Subject's full name
        contact_number: str | Subject's phone number
        new_date: str | Today's date, in practice
    """
    
    with sqlite3.connect(os.path.join(here, "jm.db")) as connection:
        cursor = connection.cursor()

        if variable_name == "intro_text":
            cursor.execute("""
            UPDATE participants
            SET intro_text = (?)
            WHERE name = (?) AND phone_number = (?);
            """, (new_date, full_name, contact_number))

        elif variable_name == "rem1":
            cursor.execute("""
            UPDATE participants
            SET rem1 = (?)
            WHERE name = (?) AND phone_number = (?);
            """, (new_date, full_name, contact_number))

        elif variable_name == "rem2":
            cursor.execute("""
            UPDATE participants
            SET rem2 = (?)
            WHERE name = (?) AND phone_number = (?);
            """, (new_date, full_name, contact_number))

        elif variable_name == "rem3":
            cursor.execute("""
            UPDATE participants
            SET rem3 = (?)
            WHERE name = (?) AND phone_number = (?);
            """, (new_date, full_name, contact_number))

        elif variable_name == "rem4":
            cursor.execute("""
            UPDATE participants
            SET rem4 = (?)
            WHERE name = (?) AND phone_number = (?);
            """, (new_date, full_name, contact_number))

        elif variable_name == "pay1":
            cursor.execute("""
            UPDATE participants
            SET pay1 = (?)
            WHERE name = (?) AND phone_number = (?);
            """, (new_date, full_name, contact_number))

        elif variable_name == "rem5":
            cursor.execute("""
            UPDATE participants
            SET rem5 = (?)
            WHERE name = (?) AND phone_number = (?);
            """, (new_date, full_name, contact_number))

        elif variable_name == "rem6":
            cursor.execute("""
            UPDATE participants
            SET rem6 = (?)
            WHERE name = (?) AND phone_number = (?);
            """, (new_date, full_name, contact_number))

        elif variable_name == "pay2":
            cursor.execute("""
            UPDATE participants
            SET pay2 = (?)
            WHERE name = (?) AND phone_number = (?);
            """, (new_date, full_name, contact_number))

        elif variable_name == "rem7":
            cursor.execute("""
            UPDATE participants
            SET rem7 = (?)
            WHERE name = (?) AND phone_number = (?);
            """, (new_date, full_name, contact_number))

        elif variable_name == "rem8":
            cursor.execute("""
            UPDATE participants
            SET rem8 = (?)
            WHERE name = (?) AND phone_number = (?);
            """, (new_date, full_name, contact_number))

        elif variable_name == "pay3":
            cursor.execute("""
            UPDATE participants
            SET pay3 = (?)
            WHERE name = (?) AND phone_number = (?);
            """, (new_date, full_name, contact_number))
