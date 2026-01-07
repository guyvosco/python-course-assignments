from utilities import (
    fetch_text,
    parse_readme,
    build_subjects_text_from_github_api,
    parse_subjects,
    add_deadline_deltas,
    make_submissions_status_table,
    print_per_assignment_summary,
    plot_on_time_distributions,
    plot_subject_format_popularity,
    make_student_habits_table,
)
import pandas as pd

def main():
    github_user = "Code-Maven"
    github_repo = "wis-python-course-2025-10"
    branch = "main"

    print("=" * 80)
    print("WIS Python Course — Assignment Submission Report")
    print(f"Repository: {github_user}/{github_repo} (branch: {branch})")
    print("=" * 80)

    # --- Load README (roster + deadlines) ---
    readme_url = f"https://raw.githubusercontent.com/{github_user}/{github_repo}/{branch}/README.md"
    readme_text = fetch_text(readme_url)
    roster, deadlines = parse_readme(readme_text)

    assignment_names = sorted(deadlines.keys(), key=lambda s: int(s[3:]) if s.lower().startswith("day") else s)

    print(f"  Students found: {len(roster)}")
    print(f"  Assignments found: {len(assignment_names)}")

    # --- Build subjects text from GitHub API ---
    # subjects_url = f"https://raw.githubusercontent.com/{github_user}/{github_repo}/{branch}/day09/subjects.txt"
    # subjects_text = fetch_text(subjects_url)
    subjects_text = build_subjects_text_from_github_api(github_user, github_repo)

    # --- Parse submissions + add deltas ---
    submissions = parse_subjects(subjects_text, roster, assignment_names)
    submissions = add_deadline_deltas(submissions, deadlines)

    unknown_students = submissions.get("UNKNOWN", {})
    if unknown_students:
        print(f"  WARNING: {len(unknown_students)} issues could not be matched to a student (stored under 'UNKNOWN').")

    # --- Build and print table ---
    header, rows = make_submissions_status_table(roster, assignment_names, submissions)
    df = pd.DataFrame(rows, columns=header)
    print("\nStatus Table (On-time / Late / Missing)\n")
    print(df.to_markdown(index=False))

    # --- Per-assignment summary ---
    print("\nPer-assignment Summary")
    print("-" * 80)

    assignment_summary = print_per_assignment_summary(roster, assignment_names, submissions)
    for a in assignment_names:
        on_time, late, missing, unchecked = assignment_summary[a]
        print(f"{a}: {on_time} on-time, {late} late, {missing} missing ({unchecked} unchecked issues).")
    
    # --- Plots ---
    plot_on_time_distributions(submissions)
    plot_subject_format_popularity(submissions, assignment_names=list(deadlines.keys()))

    # --- Student habits table ---
    header, rows = make_student_habits_table(roster, submissions)
    df = pd.DataFrame(rows, columns=header)
    print("\nStudent Submission Habits (Average Submission Time (before deadline) and Formats Used)\n")
    print(df.to_markdown(index=False))

if __name__ == "__main__":
    main()
