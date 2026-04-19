import json

import requests
import streamlit as st


st.set_page_config(page_title="JD Extraction Studio", layout="wide")
st.title("JD Extraction Studio")
st.caption("Upload a job description PDF or DOCX and get structured JD extraction output.")

jd_backend_url = st.sidebar.text_input(
    "JD Backend URL",
    value="http://localhost:8001/jdParse",
)

uploaded_jd = st.file_uploader(
    "Upload JD PDF or DOCX",
    type=["pdf", "docx"],
    key="jd_upload",
)

if uploaded_jd and st.button("Analyze JD", key="jd_analyze"):
    with st.spinner("Extracting JD..."):
        content_type = (
            "application/pdf"
            if uploaded_jd.name.lower().endswith(".pdf")
            else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        files = {
            "file": (
                uploaded_jd.name,
                uploaded_jd.getvalue(),
                content_type,
            )
        }
        response = requests.post(jd_backend_url, files=files, timeout=600)
        if response.status_code != 200:
            st.error(f"Request failed: {response.status_code}")
            st.code(response.text)
        else:
            data = response.json()
            jd_data = data.get("jd_data") or {}
            mandatory_skills = jd_data.get("mandatory_skills") or {}
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Verdict", data.get("verdict", "-"))
            c2.metric("Reflection Loops", data.get("reflection_loop", 0))
            c3.metric("Role Title", jd_data.get("role_title", "-"))
            c4.metric(
                "Mandatory Skill Buckets",
                sum(1 for value in mandatory_skills.values() if value),
            )

            left, right = st.columns(2)
            with left:
                st.subheader("JD Summary")
                st.json(
                    {
                        "role_title": jd_data.get("role_title"),
                        "company_name": jd_data.get("company_name"),
                        "job_type": jd_data.get("job_type"),
                        "job_level": jd_data.get("job_level"),
                        "work_mode": jd_data.get("work_mode"),
                        "location": jd_data.get("location"),
                        "min_years_experience": jd_data.get("min_years_experience"),
                        "max_years_experience": jd_data.get("max_years_experience"),
                        "degree_required": jd_data.get("degree_required"),
                        "salary_range": jd_data.get("salary_range"),
                    }
                )
                st.subheader("Responsibilities")
                st.json(jd_data.get("summary_responsibilities"))
            with right:
                st.subheader("Mandatory Skills")
                st.json(mandatory_skills)
                st.subheader("Optional Skills")
                st.json(jd_data.get("optional_skills"))

            st.subheader("Judge Results")
            st.json(data.get("judge_results"))
            st.subheader("Full Output")
            st.code(json.dumps(data, indent=2), language="json")
