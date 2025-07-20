import streamlit as st
import os
import tempfile
import fitz  # PyMuPDF
import pandas as pd
import datetime
import plotly.express as px
from utils.api import call_openrouter_api, trim_cv
from utils.parser import extract_pdf_text
from utils.analyzer import generate_prompt, extract_number, extract_between

st.set_page_config(page_title="HR AI - Candidate Analyzer", layout="wide")
st.markdown(open("utils/styles.css").read(), unsafe_allow_html=True)
st.title("🧠 All-in-One AI HR Assistant")

job_title = st.text_input("🎯 Hiring For (Job Title / Role)")
job_description = st.text_area("📌 Job Description or Role Requirements", height=200)
custom_threshold = st.slider("📈 Minimum Fit Score Required", 0, 100, 50)
uploaded_files = st.file_uploader("📁 Upload candidate CVs (PDF)", type=["pdf"], accept_multiple_files=True)
process_button = st.button("🚀 Analyze Candidates")

skill_map = {
    "Data Scientist": ["Python", "Machine Learning", "Statistics", "Data Analysis"],
    "Frontend Developer": ["HTML", "CSS", "JavaScript", "React"],
    "HR Manager": ["Recruitment", "Onboarding", "HR Policies", "Employee Relations"],
}

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
            score = extract_number(extract_between(ai_response, "Score:"))
            rec = extract_between(ai_response, "Final Verdict:", "\n")
            match_pct = extract_number(extract_between(ai_response, "Skill Match Percentage:"))
            exp_years = extract_between(ai_response, "Experience Years:", "\n")
            strengths = extract_between(ai_response, "Top 3 Strengths:", "Red Flags")
            red_flags = extract_between(ai_response, "Red Flags", "Justify")
            justification = extract_between(ai_response, "Justify role fit:", "If not recommended")
            why_not = extract_between(ai_response, "If not recommended, explain why:", "Final Verdict")
            hiring_line = extract_between(ai_response, "Provide a one-line recommendation:")
            summary_data = extract_between(ai_response, "Summarize key insights and data extracted from resume")

            results.append({
                "Candidate": name,
                "Score": score,
                "Recommendation": rec,
                "Skill Match %": match_pct,
                "Experience (Years)": exp_years,
                "Top Strengths": strengths,
                "Red Flags": red_flags,
                "Fit Justification": justification,
                "Why Not Selected": why_not,
                "AI Recommendation": hiring_line,
                "Resume Summary": summary_data,
                "Full AI Analysis": ai_response
            })

        if results:
            df = pd.DataFrame(results)
            df["Score"] = pd.to_numeric(df["Score"], errors="coerce")
            filtered_df = df[df["Score"] >= custom_threshold]
            best_df = df[df["Score"] == df["Score"].max()]

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
                        st.code(row["Full AI Analysis"], language="markdown")

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
            st.download_button("📥 Download All Filtered Candidates", data=filtered_df.to_csv(index=False).encode("utf-8"), file_name=f"Filtered_Candidates_{timestamp}.csv", mime="text/csv")
            st.download_button("🌟 Download Best Candidate(s)", data=best_df.to_csv(index=False).encode("utf-8"), file_name=f"Best_Candidate_{timestamp}.csv", mime="text/csv")
    st.balloons()
else:
    if process_button:
        st.error("⚠️ Please fill in all required fields.")
