from app.services.profile_extractor import extract_profile_from_cv

cv_text = """
Python developer with 2 years experience.
Worked with SQL, FastAPI, data analysis.
Looking for remote data analyst roles.
"""

profile = extract_profile_from_cv(cv_text)

print(profile)