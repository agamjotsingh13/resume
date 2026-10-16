from collections import Counter

from Src.job_recommender import recommend_jobs
from Src.resume_utils import analyze_resume_text


def get_improvement_skills(recommendations, top_jobs=3):
    missing_skill_counts = Counter()
    for recommendation in recommendations[:top_jobs]:
        missing_skill_counts.update(recommendation["missing_skills"])
    return [skill for skill, _ in missing_skill_counts.most_common(8)]


def analyze_resume(resume_text):
    result = analyze_resume_text(resume_text)
    result["recommendations"] = recommend_jobs(result["skills"])
    result["improvement_skills"] = get_improvement_skills(result["recommendations"])
    return result
