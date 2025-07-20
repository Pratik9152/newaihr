import re

def generate_prompt(cv_text, job_title, job_description, skill_map):
    role_skills = skill_map.get(job_title, [])
    skills_required = ", ".join(role_skills) if role_skills else "[Let AI infer skills]"
    return f"""
We are hiring for the role: {job_title}

Job Description:
{job_description}

Key Skills Expected:
{skills_required}

Resume:
{cv_text}

Evaluate:
1. Score out of 100 for fit.
2. Skill Match Percentage.
3. Experience Years.
4. Top 3 Strengths.
5. Red Flags or concerns.
6. Justify role fit.
7. If not recommended, explain why.
8. Final Verdict: Strong Fit / Moderate Fit / Not Recommended.
9. One-line recommendation: Should this candidate be hired or not and why.
10. Key insights: education, certifications, location, tools used, etc.

Respond in structured markdown.
"""

def extract_number(text):
    match = re.search(r"\d+", text)
    return int(match.group()) if match else None

def extract_between(text, start_key, end_key=None):
    try:
        pattern = re.escape(start_key) + r"(.*?)(?=" + re.escape(end_key) + r"|$)" if end_key else re.escape(start_key) + r"(.*)"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else "N/A"
    except Exception:
        return "N/A"
