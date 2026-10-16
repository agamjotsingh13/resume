import ast
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupShuffleSplit

from Src.ml_match_model import MODEL_PATH, build_pair_features, create_model


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "Data" / "resume_data.csv"
CANDIDATE_COLUMNS = [
    "career_objective",
    "skills",
    "educational_institution_name",
    "degree_names",
    "passing_years",
    "major_field_of_studies",
    "professional_company_names",
    "positions",
]


def parse_skills(value):
    if pd.isna(value):
        return []
    try:
        parsed = ast.literal_eval(value) if isinstance(value, str) else value
    except (ValueError, SyntaxError):
        return []
    return parsed if isinstance(parsed, list) else []


def parse_required_skills(value):
    if pd.isna(value):
        return []
    return [item.strip().lower() for item in str(value).split("\n") if item.strip()]


def load_training_data():
    data = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
    data.columns = data.columns.str.strip().str.replace("\ufeff", "", regex=False)
    data["resume_skills"] = data["skills"].apply(parse_skills)
    data["required_skills"] = data["skills_required"].apply(parse_required_skills)
    data["candidate_id"] = data[CANDIDATE_COLUMNS].fillna("").astype(str).agg("|".join, axis=1)
    data = data[
        data["resume_skills"].map(bool)
        & data["required_skills"].map(bool)
        & data["matched_score"].notna()
    ].copy()
    features = [
        build_pair_features(row.resume_skills, row.job_position_name, row.required_skills)
        for row in data.itertuples()
    ]
    feature_data = pd.DataFrame(features, index=data.index)
    return data, feature_data


def main():
    data, features = load_training_data()
    splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_indices, test_indices = next(
        splitter.split(features, data["matched_score"], groups=data["candidate_id"])
    )
    model = create_model()
    model.fit(features.iloc[train_indices], data["matched_score"].iloc[train_indices])
    predictions = model.predict(features.iloc[test_indices]).clip(0, 0.97)
    actual = data["matched_score"].iloc[test_indices]
    mae = mean_absolute_error(actual, predictions)
    rmse = mean_squared_error(actual, predictions) ** 0.5
    r2 = r2_score(actual, predictions)
    print(f"Training rows: {len(train_indices)}")
    print(f"Test rows: {len(test_indices)}")
    print(f"Unique candidates: {data['candidate_id'].nunique()}")
    print(f"MAE: {mae:.4f} ({mae * 100:.2f} percentage points)")
    print(f"RMSE: {rmse:.4f}")
    print(f"R2: {r2:.4f}")
    role_means = data.iloc[train_indices].groupby("job_position_name")["matched_score"].mean()
    baseline_predictions = (
        data.iloc[test_indices]["job_position_name"]
        .map(role_means)
        .fillna(data.iloc[train_indices]["matched_score"].mean())
        .to_numpy()
        .clip(0, 0.97)
    )
    baseline_mae = mean_absolute_error(actual, baseline_predictions)
    print(f"Role-average baseline MAE: {baseline_mae:.4f}")
    model.fit(features, data["matched_score"])
    joblib.dump(model, MODEL_PATH)
    print(f"Saved model: {MODEL_PATH.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()
