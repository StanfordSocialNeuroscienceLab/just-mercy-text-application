#!/bin/python3
import pandas as pd
import os, sqlite3


##########


class ParseSubjects:
    def __init__(self, app_path, file):

        self.file = file
        self.database_path = os.path.join(app_path, "jm.db")

    def load_file(self):
        if ".csv" in self.file:
            return pd.read_csv(self.file)

        elif ".xlsx" in self.file:
            return pd.read_excel(self.file, engine="openpyxl")

    def push_to_database(self, cursor, name, number, date):

        query = """
            INSERT INTO participants (name,phone_number,date_of_study)
            VALUES (?,?,?);
            """

        cursor.execute(query, (name, number, date))

    def clean_file(self):
        file = self.load_file()

        column_targets = ["subject_name", "phone_number", "date_of_study"]

        try:
            file = file.loc[:, column_targets]
        except:
            raise ValueError(
                f"Check column names - we need the following: {column_targets}"
            )

        file.dropna(inplace=True)

        def clean_phone_number(x):
            return x.replace("-", "").replace("+1", "").strip()

        def clean_name(x):
            return x.title().strip()

        file["subject_name"] = file["subject_name"].apply(lambda x: clean_name(x))
        file["phone_number"] = file["phone_number"].apply(
            lambda x: clean_phone_number(x)
        )

        return file

    def run(self):
        file = self.clean_file()

        with sqlite3.connect(self.database_path) as connection:
            cursor = connection.cursor()

            for ix, name in enumerate(file["subject_name"]):

                phone = file["phone_number"][ix]
                date = file["date_of_study"][ix]

                self.push_to_database(cursor=cursor, name=name, number=phone, date=date)
