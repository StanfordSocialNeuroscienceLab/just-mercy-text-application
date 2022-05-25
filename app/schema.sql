CREATE TABLE participants (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 name TEXT NOT NULL,
 phone_number TEXT NOT NULL,
 date_of_study DATETIME NOT NULL,
 first_contact TEXT DEFAULT "INCOMPLETE",
 second_contact TEXT DEFAULT "INCOMPLETE",
 third_contact TEXT DEFAULT "INCOMPLETE",
 ignore TEXT DEFAULT "False"
)