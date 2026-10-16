import re


SKILLS = [
    "python", "java", "c++", "c#", "sql", "excel", "power bi", "tableau",
    "machine learning", "deep learning", "pandas", "numpy", "scikit-learn",
    "tensorflow", "pytorch", "html", "css", "javascript", "typescript",
    "react", "angular", "vue", "node", "fastapi", "django", "flask",
    "aws", "gcp", "azure", "docker", "kubernetes", "git", "linux",
    "data analysis", "data science", "data visualization", "business analysis",
    "natural language processing", "artificial intelligence", "mongodb", "mysql",
    "postgresql", "redis", "cloud", "devops", "rest api", "project management",
    "agile", "scrum", "c", "data structures and algorithms", "problem solving",
    "graphic designing", "video editing", "public speaking",
]


SKILL_LABELS = {
    "sql": "SQL", "css": "CSS", "html": "HTML", "aws": "AWS", "gcp": "GCP",
    "c": "C", "c++": "C++", "c#": "C#", "mysql": "MySQL", "mongodb": "MongoDB",
    "postgresql": "PostgreSQL", "pytorch": "PyTorch", "tensorflow": "TensorFlow",
    "javascript": "JavaScript", "typescript": "TypeScript", "fastapi": "FastAPI",
    "numpy": "NumPy", "scikit-learn": "scikit-learn", "power bi": "Power BI",
    "rest api": "REST API", "devops": "DevOps", "ml": "ML", "node": "Node.js",
    "data structures and algorithms": "Data Structures & Algorithms", "r": "R",
}


SECTIONS = ["education", "technical skills", "experience", "projects", "activities"]


def skill_label(skill):
    return SKILL_LABELS.get(skill.lower(), skill.title())


def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9+#.\s-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_skills(resume_text):
    text = clean_text(resume_text)
    found = set()

    for skill in SKILLS:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"
        if re.search(pattern, text):
            found.add(skill)

    return sorted(found)


def calculate_resume_score(resume_text, skills):
    text = resume_text.lower()

    skill_points = min(len(skills) / 12 * 40, 40)
    section_points = 8 * sum(1 for section in SECTIONS if section in text)

    word_count = len(text.split())
    length_points = 0
    for minimum, points in [(300, 20), (200, 15), (100, 10), (50, 5)]:
        if word_count >= minimum:
            length_points = points
            break

    return round(min(skill_points + section_points + length_points, 100), 1)


def analyze_resume_text(resume_text):
    skills = extract_skills(resume_text)
    return {
        "clean_text": clean_text(resume_text),
        "skills": skills,
        "total_skills": len(skills),
        "resume_score": calculate_resume_score(resume_text, skills),
    }
