# My Data Science Projects
Medical Data Normalization & Fuzzy Matching

Overview
This Python script automates the cleaning, standardization, and matching of medical diagnoses using fuzzy string matching and an abbreviation dictionary. It processes raw patient diagnosis data, replaces abbreviations, and applies fuzzy matching (Levenshtein distance) to improve consistency before storing the results in an SQLite database.

Features
Data Cleaning: Expands abbreviations and corrects inconsistencies in medical diagnoses.
Fuzzy Matching: Uses fuzzywuzzy (or rapidfuzz) to match similar diagnoses from different sources.
SQLite Integration: Reads and updates patient records efficiently in a structured database.
Customizable Abbreviation Dictionary: Easily extendable to handle additional medical terminology variations.

Why This Matters
In clinical research and medical data management, inconsistencies in diagnosis data can affect analysis and decision-making. This tool streamlines data preparation, ensuring better accuracy for downstream processes like querying, reporting, and machine learning applications.

About the Author
👋 GG (GitHub: ggphysician) is an Emergency Medicine physician, clinical researcher, and data professional with expertise in clinical trials, data automation, and medical informatics.

Founder of GP Data Services, a company focused on data governance & automation in clinical research.
Experience in Python, SQL, data parsing, and automation for research and business applications.
Passionate about solving inefficiencies in clinical workflows using technology and AI-driven solutions.

Future Plans
This project is part of a growing portfolio of automation tools. Planned enhancements:
✅ Support for additional medical data formats
✅ Integration with OCR tools for scanned medical records
✅ Implementation of ML-driven diagnosis categorization
