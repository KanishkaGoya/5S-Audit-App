import streamlit as st
import sqlite3
import os
from datetime import datetime

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

conn = sqlite3.connect("audit.db", check_same_thread=False)
cursor = conn.cursor()

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS audits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    audit_date TEXT,
    plant TEXT,
    division TEXT,
    divisional_head TEXT,
    department_head TEXT,
    audit_area TEXT,
    audit_line TEXT,
    auditee TEXT,
    auditor TEXT,
    jh_leader TEXT,
    s_type TEXT,
    rating INTEGER,
    observation TEXT,
    image_paths TEXT
)
""")
conn.commit()

st.title("5S Audit App")

audit_date = st.date_input("Audit Date")

plant = st.selectbox(
    "Plant",
    ["Jaipur", "Newai", "Savli", "Bagru"]
)

division = st.selectbox(
    "Division",
    ["BB", "TRB", "RB", "LDB", "Quality", "Maintainance"]
)

divisional_head = st.text_input("Divisional Head")
department_head = st.text_input("Department Head")
audit_area = st.text_input("Audit Area")
audit_line = st.text_input("Audit Line/Area/Office")
auditee = st.text_input("Auditee")
auditor = st.text_input("Auditor")
jh_leader = st.text_input("JH Leader")

s_type = st.selectbox(
    "Select S",
    ["1S", "2S", "3S", "4S", "5S"]
)

rating = st.slider("Rating", 1, 5)

observation = st.text_area("Observation")

uploaded_files = st.file_uploader(
    "Upload/Capture Images",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

if st.button("Save Audit"):
    saved_paths = []

    for file in uploaded_files:
        filename = f"{datetime.now().timestamp()}_{file.name}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        with open(filepath, "wb") as f:
            f.write(file.getbuffer())

        saved_paths.append(filepath)

    image_paths = ",".join(saved_paths)

    cursor.execute("""
    INSERT INTO audits (
        audit_date, plant, division, divisional_head,
        department_head, audit_area, audit_line,
        auditee, auditor, jh_leader,
        s_type, rating, observation, image_paths
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        str(audit_date),
        plant,
        division,
        divisional_head,
        department_head,
        audit_area,
        audit_line,
        auditee,
        auditor,
        jh_leader,
        s_type,
        rating,
        observation,
        image_paths
    ))

    conn.commit()
    st.success("Audit Saved Successfully!")