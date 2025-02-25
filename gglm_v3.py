import sqlite3
import json
import csv
import datetime
import re
import tkinter as tk
import time
from tkinter import filedialog
from rapidfuzz import process, fuzz


# File name for export
output_file = '47k_cleaned_python_confirm.csv'

conn = sqlite3.connect('47k.sqlite')
cur = conn.cursor()

# Build SQLite tables
cur.executescript('''
DROP TABLE IF EXISTS Subject;
DROP TABLE IF EXISTS Medical;
DROP TABLE IF EXISTS Multi;

CREATE TABLE Subject (
    patient_key INTEGER NOT NULL PRIMARY KEY UNIQUE,
    first_name TEXT,
    last_name TEXT
);
                  
CREATE TABLE Medical (
    multi_record TEXT NOT NULL PRIMARY KEY UNIQUE,
    diagnosis TEXT NOT NULL,
    start TEXT,
    stop TEXT
);
                  
CREATE TABLE Multi (
    patient_key_id INTEGER,
    multi_record_id TEXT,
    id INTEGER, PRIMARY KEY (patient_key_id, multi_record_id)
);
''')

# Medical abbreviations dictionary
abbreviation_dict = {
    "af": "Atrial fibrillation",
    "bph": "Benign prostatic hyperplasia",
    "cabg": "Coronary artery bypass",
    "cervical disc disorders": "Cervical disc degeneration",
    "chf" :"Congestive Heart Failure",
    "copd" : "Chronic Obstructive pulmonary disease",
    "contact dermatitis" : "Dermatitis contact",
    "dvt": "Deep vein thrombosis",
    "gerd": "Gastroesophageal reflux disease",
    "high cholesterol": "Hypercholesterolemia",
    "htn": "Hypertension",
    "mi": "Myocardial infarction",
    "other diseases of liver - fatty liver": "Nonalcoholic fatty liver disease",
    "seasonal allergies" : "Seasonal allergy",
    "t2dm": "Type 2 diabetes mellitus",
    "type 2 diabetes": "Type 2 diabetes mellitus",
    "t1dm": "Type 1 diabetes mellitus",

}

# Function to convert dates
def convert_date(date_str):
    try:
        parsed_date = datetime.datetime.strptime(date_str, "%d-%b-%y").date()
        return parsed_date.strftime("%Y-%m-%d")
    except ValueError:
        return None

# Function to clean diagnosis by removing ICD codes
def clean_diagnosis(diagnosis_dirty):
    pattern = r'^\s*"?[A-Za-z]\d{1,2}[\t\s]*'
    diagnosis_clean = re.sub(pattern, '', diagnosis_dirty).strip().strip('"').strip("'")  
    return diagnosis_clean

# Function to select CSV file using Tkinter
def select_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    return file_path

# Function to remove and clean the " jr" from patient first name
def clean_commas(line):
    # Remove misplaced commas before splitting (e.g., "Applegate, Jr." → "Applegate Jr.")
    line = re.sub(r',\s*(Jr|Sr)\b', r' \1', line)  # Fix misplaced commas before Jr/Sr
    return line
    

# Load CSV data-----------------------
fname = select_file()
if not fname:
    print("No file selected. Exiting.")
    exit()

fh = open(fname, encoding='utf-8-sig')

medical_data = {}

#Trying to batch commits
batch_size = 500
count = 0

for line in fh:
    line = clean_commas(line)
    pieces = line.strip().split(',')
    
    if not pieces[0].strip():
        continue

    first_name = pieces[2]
    last_name = pieces[3]
    patient_key = pieces[4]
    multi_record = pieces[8]

    # looking for bugs in data pieces and sqlite
    # #print(f"Attempting to insert: {patient_key}, {first_name}, {last_name}")

    # Insert into Subject table
    cur.execute('''INSERT OR IGNORE INTO Subject (patient_key, first_name, last_name)
        VALUES (?, ?, ?)''', (patient_key, first_name, last_name))
    
    # Insert into Multi table
    cur.execute('''INSERT OR IGNORE INTO Multi (patient_key_id, multi_record_id)
        VALUES (?, ?)''', (patient_key, multi_record))
    
    count += 1
    if count % batch_size == 0:  #is count a multiple of batch size
        print(f"Committing {count} records...")
        conn.commit()
        time.sleep(.01) #give time for commit
        print(f"Committed {count} records sucessfully")


    if multi_record not in medical_data:
        medical_data[multi_record] = {"diagnosis": None, "start": None, "stop": None}

    category = pieces[5].strip()
    value = pieces[7].strip()

    if category in ["Reason", "Finding"] and value and value not in ["[Not Done]", ""]:
        cleaned_diagnosis = clean_diagnosis(value)
        # identify specific values in the diagnosis to replace (CABG anywhere is changed to "Coronary artery bypass")
        if "cabg" in cleaned_diagnosis.lower():
            cleaned_diagnosis = "Coronary artery bypass"
        if "cardiac stent" in cleaned_diagnosis.lower() and "placement" in cleaned_diagnosis.lower():
            cleaned_diagnosis = "Corononary arterial stent insertion"
         # Expand abbreviations if found
        else:
            cleaned_diagnosis = abbreviation_dict.get(cleaned_diagnosis.lower(), cleaned_diagnosis)
        medical_data[multi_record]["diagnosis"] = cleaned_diagnosis

    elif category == "Start":
        start_date = convert_date(value)
        if start_date:
            medical_data[multi_record]["start"] = start_date

    elif category == "Stop":
        medical_data[multi_record]["stop"] = "Ongoing" if value.lower() == 'ongoing' else convert_date(value)

# Remove entries without a diagnosis
medical_data = {k: v for k, v in medical_data.items() if v.get("diagnosis")}

# Insert data into Medical table
for multi_record, data in medical_data.items():
    cur.execute('''INSERT OR IGNORE INTO Medical (multi_record, diagnosis, start, stop)
        VALUES (?, ?, ?, ?)''', (multi_record, data["diagnosis"], data["start"], data["stop"]))

# Fetch unique crio_diagnosis values - iterating through the table in SQlite to then fetch all rows and add them to crio_diagnosis list of tupples
cur.execute("SELECT DISTINCT crio_diagnosis FROM CRIO")
crio_diagnoses = [row[0] for row in cur.fetchall()]

# Fetch all Medical diagnoses - iterating through table in SQlite to fetch all rows and add tuples to medical_entries
cur.execute("SELECT multi_record, diagnosis FROM Medical")
medical_entries = cur.fetchall()


# Apply fuzzy matching to standardize Medical.diagnosis
for multi_record, diagnosis in medical_entries:
    best_match, score, _ = process.extractOne(diagnosis, crio_diagnoses, scorer=fuzz.token_sort_ratio)
    
    if score >= 80:  # Only update if match confidence is high
        cur.execute("UPDATE Medical SET diagnosis = ? WHERE multi_record = ?", (best_match, multi_record))

# Join Tables to create CRIO-ready output
try:
    cur.execute('''
SELECT 
    Multi.patient_key_id, 
    Crio.crio_diagnosis, 
    Medical.start, 
    Medical.stop, 
    Crio.crio_key
FROM 
    Medical
INNER JOIN 
    CRIO ON LOWER(Medical.diagnosis) = LOWER(Crio.crio_diagnosis)
INNER JOIN 
    Multi ON Medical.multi_record = Multi.multi_record_id;
    ''')

    results = cur.fetchall()

    # Define CSV headers
    headers = ["patient_id", "Finding", "Start", "Stop", "crio_key"]

    # Export to CSV
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers) # Writes column headers
        writer.writerows(results) # Write data rows
    
    print(f"Exported Successfully to {output_file} 💾")


except sqlite3.Error as e:
    print(f"An error occurred: {e}")
except Exception as e:
    print(f"A general error occurred: {e}")

print("Final commit for remaining records...")
conn.close()
print(f"Final commit for {count} total records.")

#confirm closure of SQL
print("Database connection closed successfully ✅ ")



