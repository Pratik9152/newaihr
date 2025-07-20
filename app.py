import streamlit as st
import os
import tempfile
import fitz  # PyMuPDF
import pandas as pd
import datetime
import plotly.express as px
import json

from api import call_openrouter_api, trim_cv
from parser import extract_pdf_text
from analyzer import generate_prompt

# Page Setup and Styles
st.set_page_config(page_title="HR AI - Candidate Analyzer", layout="wide")

with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("🧠 All-in-One AI HR Assistant")

# Inputs
job_title = st.text_input("🎯 Hiring For (Job Title / Role)")
job_description = st.text_area("📌 Job Description or Role Requirements", height=200)
custom_threshold = st.slider("📈 Minimum Fit Score Required", 0, 100, 50)
uploaded_files = st.file_uploader("📁 Upload candidate CVs (PDF only)", type=["pdf"], accept_multiple_files=True)
process_button = st.button("🚀 Analyze Candidates")

# Predefined skills (extend as needed)
skill_map = {
    "Data Scientist": ["Python", "Machine Learning", "Statistics", "Data Analysis"],
    "Frontend Developer": ["HTML", "CSS", "JavaScript", "React"],
    "HR Manager": ["Recruitment", "Onboarding", "HR Policies", "Employee Relations"],
}

# Processing Logic
if process_button and job_description and uploaded_files:
    with st.spinner("🤖 AI analyzing candidates. Please wait..."):
        candidates = []
        with tempfile.TemporaryDirectory() as tmpdir:
            for file in uploaded_files:
                path = os.path.join(tmpdir, file.name)
                with open(path, "wb") as f:
                    f.write(file.read())
                text = extract_pdf_text(path)
                candidates.append((file.name, trim_cv(text)))

        results = []
        for name, cv_text in candidates:
            prompt = generate_prompt(cv_text, job_title, job_description, skill_map)
            ai_response = call_openrouter_api(prompt)

            try:
                result = json.loads(ai_response)
            except Exception:
                st.error(f"❌ Failed to parse AI response for: {name}")
                st.code(ai_response)
                result = {}

            results.append({
                "Candidate": name,
                "Score": result.get("Score", 0),
                "Recommendation": result.get("Final Verdict", "N/A"),
                "Skill Match %": result.get("Skill Match Percentage", 0),
                "Experience (Years)": result.get("Experience Years", "N/A"),
                "Top Strengths": result.get("Top Strengths", "N/A"),
                "Red Flags": result.get("Red Flags", "N/A"),
                "Fit Justification": result.get("Fit Justification", "N/A"),
                "Why Not Selected": result.get("Why Not Selected", "N/A"),
                "AI Recommendation": result.get("One Line Recommendation", "N/A"),
                "Resume Summary": result.get("Resume Summary", "N/A"),
                "Full AI Analysis": ai_response
            })

        if results:
            df = pd.DataFrame(results)
            df["Score"] = pd.to_numeric(df["Score"], errors="coerce")
            filtered_df = df[df["Score"] >= custom_threshold]
            best_df = df[df["Score"] == df["Score"].max()]

            if filtered_df.empty:
                filtered_df = df
                st.warning("⚠️ No candidates met the threshold. Showing all instead.")

            st.success("✅ AI Analysis Complete")
            st.subheader("📊 Candidate Insights Dashboard")
            st.markdown(f"**🧑‍💼 {len(filtered_df)} candidates meet the criteria.**")

            st.plotly_chart(px.bar(filtered_df, x="Candidate", y="Score", color="Recommendation", text="Score"), use_container_width=True)
            st.plotly_chart(px.pie(filtered_df, names="Recommendation"), use_container_width=True)

            for _, row in filtered_df.iterrows():
                with st.expander(f"📌 {row['Candidate']} — Score: {row['Score']} — {row['Recommendation']}"):
                    st.markdown(f"### 🟢 AI Recommendation: {row['AI Recommendation']}")
                    st.markdown(f"**Top Strengths**:\n{row['Top Strengths']}")
                    st.markdown(f"**Red Flags**:\n{row['Red Flags']}")
                    st.markdown(f"**Fit Justification**:\n{row['Fit Justification']}")
                    st.markdown(f"**Why Not Selected**: {row['Why Not Selected']}")
                    st.markdown(f"**📌 Resume Summary**:\n{row['Resume Summary']}")
                    with st.expander("📄 Full AI Response"):
                        st.code(row["Full AI Analysis"], language="json")

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
            st.download_button("📥 Download All Filtered Candidates", data=filtered_df.to_csv(index=False).encode("utf-8"), file_name=f"Filtered_Candidates_{timestamp}.csv", mime="text/csv")
            st.download_button("🌟 Download Best Candidate(s)", data=best_df.to_csv(index=False).encode("utf-8"), file_name=f"Best_Candidate_{timestamp}.csv", mime="text/csv")
    st.balloons()
else:
    if process_button:
        st.error("⚠️ Please fill in all required fields.")
