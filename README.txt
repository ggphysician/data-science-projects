This is a software designed to clean up CRIO data.

Requirements: python and SQLite
Libraries: pip install sqlite3 fuzzywuzzy rapidfuzz datetime tkinter re

Run crio_ref.py first, to build the CRIO reference database.

Then run gg_47_v3.py to select a new file to clean.

This will allow selection of a CSV file (created by CRIO) during data extraction and iterate through the file to create a cleaner CSV file for ingestion into CRIO.

End users tend to use diagnosis and dates that CRIO does not officially recognize.  This software automates the transform portion of ETL.

SQL code for final CSV

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



