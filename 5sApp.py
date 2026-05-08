import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ---------------- CONFIG ----------------
UPLOAD_FOLDER = "uploads"
EXCEL_FILE = "audit_records.xlsx"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

st.set_page_config(page_title="5S Audit App", layout="wide")
st.title("5S Audit Management App")

# ---------------- CREATE EXCEL IF NOT EXISTS ----------------
if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=[
        "Audit ID",
        "Audit Date",
        "Plant",
        "Division",
        "Divisional Head",
        "Department Head",
        "Audit Area",
        "Audit Line/Area/Office",
        "Auditee",
        "Auditor",
        "JH Leader",
        "S Type",
        "Observation",
        "Image Paths",
        "Timestamp"
    ])
    df.to_excel(EXCEL_FILE, index=False)

# ---------------- AUDIT HEADER ----------------
st.header("Audit Details")

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

# ---------------- S TYPE ----------------
s_type = st.selectbox(
    "Select S",
    ["1S", "2S", "3S", "4S", "5S"]
)

# ---------------- OBSERVATIONS ----------------
st.header("Observations")

if "observations_count" not in st.session_state:
    st.session_state.observations_count = 1

if st.button("➕ Add Observation"):
    st.session_state.observations_count += 1

observation_data = []

for i in range(st.session_state.observations_count):
    st.subheader(f"Observation {i+1}")

    obs_text = st.text_area(
        f"Observation Text {i+1}",
        key=f"obs_text_{i}"
    )

    uploaded_files = st.file_uploader(
        f"Upload/Capture Images {i+1}",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key=f"img_{i}"
    )

    observation_data.append({
        "text": obs_text,
        "files": uploaded_files
    })

# ---------------- SAVE BUTTON ----------------
if st.button("Save Audit"):
    audit_id = "AUD-" + datetime.now().strftime("%Y%m%d%H%M%S")

    existing_df = pd.read_excel(EXCEL_FILE)
    new_rows = []

    for obs in observation_data:
        saved_paths = []

        if obs["files"]:
            for file in obs["files"]:
                filename = f"{audit_id}_{file.name}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)

                with open(filepath, "wb") as f:
                    f.write(file.getbuffer())

                saved_paths.append(filepath)

        image_paths = ",".join(saved_paths)

        row = {
            "Audit ID": audit_id,
            "Audit Date": str(audit_date),
            "Plant": plant,
            "Division": division,
            "Divisional Head": divisional_head,
            "Department Head": department_head,
            "Audit Area": audit_area,
            "Audit Line/Area/Office": audit_line,
            "Auditee": auditee,
            "Auditor": auditor,
            "JH Leader": jh_leader,
            "S Type": s_type,
            "Observation": obs["text"],
            "Image Paths": image_paths,
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        new_rows.append(row)

    new_df = pd.DataFrame(new_rows)
    final_df = pd.concat([existing_df, new_df], ignore_index=True)
    final_df.to_excel(EXCEL_FILE, index=False)

    st.success(f"Audit Saved Successfully! Audit ID: {audit_id}")
