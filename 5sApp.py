import streamlit as st
import pandas as pd
import os
import zipfile
from datetime import datetime

# ---------------- CONFIG ----------------
UPLOAD_FOLDER = "Uploads"
EXCEL_FILE = "audit_records.xlsx"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

st.set_page_config(page_title="5S Audit App", layout="wide")
st.title("5S Audit Management App")

if "save_success" in st.session_state:
    st.success(st.session_state.save_success)

# ---------------- SESSION STATE ----------------
if "obs_count" not in st.session_state:
    st.session_state.obs_count = 1

if "last_saved_signature" not in st.session_state:
    st.session_state.last_saved_signature = None

# ---------------- CREATE EXCEL ----------------
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
        "Image Names",
        "Timestamp"
    ])
    df.to_excel(EXCEL_FILE, index=False)

# ---------------- AUDIT DETAILS ----------------
st.header("Audit Details")

audit_date = st.date_input("Audit Date")
plant = st.selectbox("Plant", ["Jaipur", "Newai", "Savli", "Bagru"])

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

s_type = st.selectbox("Select S", ["1S", "2S", "3S", "4S", "5S"])

# ---------------- OBSERVATIONS ----------------
st.header("Observations")

if st.button("➕ Add Observation"):
    st.session_state.obs_count += 1

observation_data = []

for i in range(st.session_state.obs_count):
    st.subheader(f"Observation {i+1}")

    obs_text = st.text_area(
        f"Observation Text {i+1}",
        key=f"text_{i}"
    )

    image_option = st.radio(
        f"Add Image for Observation {i+1}",
        ["None", "Upload from Device", "Capture from Camera"],
        horizontal=True,
        key=f"image_option_{i}"
    )

    files = []

    if image_option == "Upload from Device":
        uploaded_files = st.file_uploader(
            f"Upload Images {i+1}",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            key=f"upload_{i}"
        )

        if uploaded_files:
            files.extend(uploaded_files)

    elif image_option == "Capture from Camera":
        camera_file = st.camera_input(
            f"Capture Image {i+1}",
            key=f"camera_{i}"
        )

        if camera_file:
            files.append(camera_file)

    # Preview images
    if files:
        for file in files:
            st.image(file, caption=file.name, width=250)

    observation_data.append({
        "text": obs_text,
        "files": files
    })

# ---------------- SAVE AUDIT ----------------
if st.button("Save Audit"):

    current_signature = str({
        "audit_date": str(audit_date),
        "plant": plant,
        "division": division,
        "audit_area": audit_area,
        "audit_line": audit_line,
        "auditee": auditee,
        "auditor": auditor,
        "s_type": s_type,
        "observations": [obs["text"] for obs in observation_data]
    })

    if st.session_state.last_saved_signature == current_signature:
        st.warning("This audit is already saved.")
        st.stop()

    safe_division = division.replace(" ", "_")
    safe_area = audit_area.replace(" ", "_")
    safe_line = audit_line.replace(" ", "_")

    today_str = datetime.now().strftime("%Y%m%d")

    existing_df = pd.read_excel(EXCEL_FILE)

    today_count = existing_df[
        existing_df["Audit ID"].astype(str).str.contains(today_str, na=False)
    ].shape[0] + 1

    seq_no = str(today_count).zfill(3)

    audit_id = (
        f"{safe_division}_"
        f"{safe_area}_"
        f"{safe_line}_"
        f"AUD{today_str}{seq_no}"
    )

    rows = []

    for obs in observation_data:
        saved_files = []

        if obs["files"]:
            for file in obs["files"]:
                image_number = len(saved_files) + 1
                filename = f"{audit_id}_{image_number}.jpg"

                filepath = os.path.join(UPLOAD_FOLDER, filename)

                with open(filepath, "wb") as f:
                    f.write(file.getbuffer())

                saved_files.append(filename)

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
            "Image Names": ",".join(saved_files),
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        rows.append(row)

    new_df = pd.DataFrame(rows)
    final_df = pd.concat([existing_df, new_df], ignore_index=True)
    final_df.to_excel(EXCEL_FILE, index=False)

    st.session_state.last_saved_signature = current_signature
    st.session_state.save_success = f"Audit Saved Successfully! Audit ID: {audit_id}"

    # Clear form fields
    keys_to_keep = ["last_saved_signature", "save_success"]

    for key in list(st.session_state.keys()):
       if key not in keys_to_keep:
           del st.session_state[key]

# ---------------- DOWNLOAD EXCEL ----------------
if os.path.exists(EXCEL_FILE):
    with open(EXCEL_FILE, "rb") as file:
        st.download_button(
            label="Download Audit Records Excel",
            data=file,
            file_name="audit_records.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# ---------------- DOWNLOAD ZIP ----------------
zip_filename = "all_audit_images.zip"

with zipfile.ZipFile(zip_filename, "w") as zipf:
    for root, dirs, files in os.walk(UPLOAD_FOLDER):
        for file in files:
            file_path = os.path.join(root, file)
            zipf.write(file_path, arcname=file)

if os.path.exists(zip_filename):
    with open(zip_filename, "rb") as f:
        st.download_button(
            label="Download All Audit Images ZIP",
            data=f,
            file_name=zip_filename,
            mime="application/zip"
        )

# ---------------- IMAGE GALLERY ----------------
st.header("Uploaded Images Gallery")

image_files = os.listdir(UPLOAD_FOLDER)

if image_files:
    for img in image_files:
        img_path = os.path.join(UPLOAD_FOLDER, img)
        st.image(img_path, caption=img, width=250)
else:
    st.info("No uploaded images yet.")
