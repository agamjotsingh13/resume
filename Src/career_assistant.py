from Src.resume_utils import skill_label


def format_skills(skills):
    if not skills:
        return "none listed"
    return ", ".join(skill_label(skill) for skill in skills)


def generate_career_advice(question, result):
    question = question.lower().strip()
    best = result["recommendations"][0]

    role = best["job"]
    score = best["score"]
    matched = format_skills(best["matched_skills"])
    missing = format_skills(best["missing_skills"][:5])
    improvement = format_skills(result["improvement_skills"][:5])
    detected = format_skills(result["skills"][:8])

    if any(word in question for word in ("why", "recommended", "role")):
        return (
            f"{role} is the top match because your resume includes skills in {matched}. "
            f"The weighted skill match is {score}%. To improve coverage, review {missing}."
        )

    if any(word in question for word in ("learn", "skill", "improve")):
        return (
            f"A useful next step is to focus on {improvement}. These skills appear among "
            f"the gaps in your strongest job-profile matches, including {role}."
        )

    if any(word in question for word in ("project", "build")):
        next_skill = skill_label(best["missing_skills"][0]) if best["missing_skills"] else "an advanced topic"
        return (
            f"For {role}, build a project that demonstrates {matched}. To stretch your skills, "
            f"include a practical element involving {next_skill} and document what you built."
        )

    if any(word in question for word in ("interview", "questions")):
        return (
            f"For a {role} interview, prepare to explain how you used {matched}. Also revise "
            f"the areas not yet visible on your resume: {missing}. Support answers with a real project or example."
        )

    if any(word in question for word in ("ready", "internship")):
        return (
            f"Your resume currently shows {detected}, which gives you a starting point for {role}. "
            f"Strengthening {improvement} and adding project evidence would make your profile more specific."
        )

    if "resume" in question:
        return (
            f"Your resume already mentions {detected}. To make it clearer, describe the problem, "
            f"the tools you used, your contribution, and the result for each project. Add evidence for {improvement} as you develop them."
        )

    return (
        f"Your strongest current match is {role} at {score}%. Matching skills include {matched}. "
        f"Useful areas to work on next are {improvement}."
    )
