import sqlite3
import json
import csv
import datetime
import re

conn = sqlite3.connect('47k.sqlite')
cur = conn.cursor()


#Build SQLite tables
cur.executescript('''

DROP TABLE IF EXISTS CRIO;

CREATE TABLE CRIO (
    crio_key INTEGER NOT NULL PRIMARY KEY UNIQUE,
    crio_diagnosis TEXT
);


         ''')

print('Opening CRIO_PK File.... ')
print('Loading CSV file into database (47k.sqlite)')
name = 'CRIO_PK.csv'
fh = open(name)
encoding='utf-8-sig'


for line in fh:
    pieces = line.split(',')
    crio_key_csv = pieces[0]
    crio_diagnosis_csv = pieces[1]
    cur.execute('''INSERT OR IGNORE INTO CRIO (crio_key, crio_diagnosis)
    Values (?, ?)''', (crio_key_csv, crio_diagnosis_csv))

print('Table CRIO added to 47k.sqlite database.  ')

conn.commit()

conn.close()