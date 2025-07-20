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

Please evaluate and respond ONLY with this JSON structure. No explanation, markdown, or code block. Just plain JSON.

{{
  "Score": 0-100,
  "Skill Match Percentage": 0-100,
  "Experience Years": "string or number",
  "Top Strengths": "text",
  "Red Flags": "text",
  "Fit Justification": "text",
  "Why Not Selected": "text",
  "Final Verdict": "Strong Fit / Moderate Fit / Not Recommended",
  "One Line Recommendation": "text",
  "Resume Summary": "education, companies, tools etc."
}}

Strictly return only a valid JSON object.
"""
