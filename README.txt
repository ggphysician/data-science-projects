This is a software designed to clean up CRIO data.  It will ingest CRIO data in CSV format and be able to export clean CSV CRIO data for cleaner CRIO ingestion.

Requirements: python and SQLite

Run crio_ref.py first, to build the reference database based on CRIO nomenclature.

Then run gg_47_v3.py to select a new file to clean.

The following SQL code is used to export clean CSV data.

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



