import sqlite3
from rapidfuzz import process, fuzz

# Connect to database
conn = sqlite3.connect('47k.sqlite')
cur = conn.cursor()

# Retrieve data
cur.execute("SELECT crio_diagnosis FROM CRIO")
crio_d = [row[0].strip().lower() for row in cur.fetchall() if row[0]]

cur.execute("SELECT diagnosis FROM Medical")
medical_names = [row[0].strip().lower() for row in cur.fetchall() if row[0]]

# Function to get the best match using fuzzy logic
def get_best_match(med_name, choices):
    match = process.extractOne(med_name, choices, scorer=fuzz.token_sort_ratio, score_cutoff=85)
    if match:  # Ensure match is not None
        best_match, score, *_ = match  # Correct unpacking to avoid ValueError
        return (med_name, best_match, score)
    return None  # Return None if no match found

# Perform fuzzy matching
matches = [get_best_match(med_name, crio_d) for med_name in medical_names]
matches = [m for m in matches if m]  # Remove None matches

# Print results
for med_name, best_match, score in matches:
    print(f"Medical Diagnosis: {med_name} | Best Match: {best_match} | Similarity: {score}%")

conn.close()

#need to check further, decent