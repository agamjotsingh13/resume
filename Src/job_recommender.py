import math
import os
from functools import lru_cache

import joblib

from Src.ml_match_model import normalize_skill, predict_match_score


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "job_skill_sets.pkl")
MODEL_INFLUENCE = 0.2
MAX_MODEL_ADJUSTMENT = 4.0


def calibrate_match_score(skill_score, model_score, has_match):
    if not has_match:
        return round(float(skill_score), 2)
    adjustment = (float(model_score) - float(skill_score)) * MODEL_INFLUENCE
    adjustment = max(-MAX_MODEL_ADJUSTMENT, min(MAX_MODEL_ADJUSTMENT, adjustment))
    return round(max(0.0, min(100.0, float(skill_score) + adjustment)), 2)


@lru_cache(maxsize=1)
def load_job_profiles():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("job_skill_sets.pkl was not found in the models folder.")
    return joblib.load(MODEL_PATH)


def calculate_skill_weights(job_skill_sets):
    total_jobs = len(job_skill_sets)
    skill_job_count = {}

    for skills in job_skill_sets.values():
        for skill in {normalize_skill(item) for item in skills}:
            skill_job_count[skill] = skill_job_count.get(skill, 0) + 1

    return {
        skill: math.log((total_jobs + 1) / (count + 1)) + 1
        for skill, count in skill_job_count.items()
    }


def calculate_match_score(resume_skills, required_skills, weights):
    resume_skills = {normalize_skill(skill) for skill in resume_skills}
    required_skills = {normalize_skill(skill) for skill in required_skills}

    if not required_skills:
        return 0, [], []

    matched = resume_skills & required_skills
    missing = required_skills - resume_skills
    total_weight = sum(weights.get(skill, 1) for skill in required_skills)
    matched_weight = sum(weights.get(skill, 1) for skill in matched)
    score = matched_weight / total_weight * 100 if total_weight else 0

    return round(score, 2), sorted(matched), sorted(missing)


def recommend_jobs(resume_skills):
    profiles = load_job_profiles()
    weights = calculate_skill_weights(profiles)
    recommendations = []

    for job, required_skills in profiles.items():
        skill_score, matched, missing = calculate_match_score(
            resume_skills,
            required_skills,
            weights,
        )
        model_score = predict_match_score(resume_skills, job, required_skills)
        final_score = calibrate_match_score(skill_score, model_score, bool(matched))

        recommendations.append({
            "job": job,
            "score": final_score,
            "skill_match_score": skill_score,
            "model_score": model_score,
            "matched_skills": matched,
            "missing_skills": missing,
        })

    recommendations.sort(
        key=lambda item: (item["score"], item["skill_match_score"], item["model_score"]),
        reverse=True,
    )
    return recommendations
