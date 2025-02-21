This is a software designed to clean up CRIO data.

Requirements: python and SQLite

Run crio_ref.py first, to build the reference database.

Then run gg_47_v2.py to select a new file to clean.



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



