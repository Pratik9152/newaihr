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

Please evaluate and return only a valid JSON object like this:
{{
  "Score": 78,
  "Skill Match Percentage": 85,
  "Experience Years": "3.5",
  "Top Strengths": "Fast learner, Python, Analytical thinking",
  "Red Flags": "Short tenure in last role",
  "Fit Justification": "Has all required skills and relevant experience.",
  "Why Not Selected": "",
  "Final Verdict": "Strong Fit",
  "One Line Recommendation": "Should be hired for strong data science background.",
  "Resume Summary": "MSc in Statistics, worked at TCS, Python, Pandas, Scikit-learn"
}}

Respond only with the JSON object.
"""
