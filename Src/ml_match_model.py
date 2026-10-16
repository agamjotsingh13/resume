from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "job_match_model.joblib"
NUMERIC_FEATURES = [
    "resume_skill_count",
    "required_skill_count",
    "match_count",
    "coverage",
    "jaccard",
]
SKILL_ALIASES = {
    "data structures": "data structures and algorithms",
    "dsa": "data structures and algorithms",
    "artificialintelligence": "artificial intelligence",
    "ml": "machine learning",
    "powerbi": "power bi",
    "reactjs": "react",
    "scikit learn": "scikit-learn",
    "aws cloud": "aws",
}


def normalize_skill(skill):
    value = str(skill).lower().strip()
    return SKILL_ALIASES.get(value, value)


def build_pair_features(resume_skills, job_title, required_skills):
    resume = sorted({normalize_skill(skill) for skill in resume_skills if normalize_skill(skill)})
    required = sorted({normalize_skill(skill) for skill in required_skills if normalize_skill(skill)})
    resume_set = set(resume)
    required_set = set(required)
    matched = sorted(resume_set & required_set)
    missing = sorted(required_set - resume_set)
    match_count = len(matched)
    required_count = len(required_set)
    union_count = len(resume_set | required_set)
    model_text = (
        f"resume skills {' '.join(resume)} job title {str(job_title).lower().strip()} "
        f"required skills {' '.join(required)} matched skills {' '.join(matched)} "
        f"missing skills {' '.join(missing)}"
    )
    return {
        "model_text": model_text,
        "resume_skill_count": len(resume_set),
        "required_skill_count": required_count,
        "match_count": match_count,
        "coverage": match_count / required_count if required_count else 0.0,
        "jaccard": match_count / union_count if union_count else 0.0,
    }


def create_model():
    features = ColumnTransformer(
        [
            ("text", TfidfVectorizer(ngram_range=(1, 2), min_df=2), "model_text"),
            ("numeric", StandardScaler(), NUMERIC_FEATURES),
        ]
    )
    return Pipeline([("features", features), ("regressor", Ridge(alpha=5))])


@lru_cache(maxsize=1)
def load_match_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError("job_match_model.joblib was not found in the models folder. Run python train_model.py first.")
    return joblib.load(MODEL_PATH)


def predict_match_score(resume_skills, job_title, required_skills):
    if not resume_skills:
        return 0.0
    features = pd.DataFrame([build_pair_features(resume_skills, job_title, required_skills)])
    prediction = float(load_match_model().predict(features)[0])
    return round(min(max(prediction, 0.0), 0.97) * 100, 2)
