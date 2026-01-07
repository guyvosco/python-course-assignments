# day09 — Assignment Submission Analytics

This assignment builds a small reporting tool that analyzes students’ assignment submissions using:
- The course `README.md`
- GitHub Issues (instead of the `subjects.txt` file)

The script prints summary tables and generates plots that help understand submission behavior and subject-line conventions.

---

## What it does

1. **Fetches and parses the course README**
   - Extracts the **student roster** from the markdown table under the `## Students` section.
   - Extracts **assignment deadlines** from the “Assignment (day N)” sections and converts them into ISO timestamps (`YYYY-MM-DDTHH:MM:SSZ`).

2. **Fetches submissions from GitHub Issues**
   
    The timestamps in `subjects.txt` reflect the **last activity** on each issue rather than the **issue creation time**, which makes them unsuitable for measuring submission timing. Instead, the script queries the repository directly via the **GitHub REST API** to retrieve all issues and reconstruct the submissions list accurately.

    - Filters out pull requests (the issues endpoint may include PRs).
    - Uses each issue’s created_at as the submission time (i.e., the moment the issue was opened).

    This approach is reusable for any course repository with the same layout and conventions (a roster + deadlines in README.md, and submissions tracked via GitHub Issues).

3. **Parses each submission**
   - Student name (best-effort match against roster)
   - Assignment (e.g., `Day01`)
   - Issue status (`OPEN` / `CLOSED`)
   - Submission time
   - Subject format label (e.g., `Day## by Name`, `Assignment ## - ...`, etc.)

4. **Computes deadline deltas**
   - For each submission: `submission_time - deadline_time` (seconds + human-readable string)

5. **Outputs**
   - A per-student table: `On-time / Late / Missing` per assignment, plus totals.
   - Per-assignment single-line summary:
        ```
        Day##: X on-time, Y late, Z missing (W unchecked issues).
        ```
   - Plots:
     - On-time submissions by weekday
     - On-time submissions by hour of day
     - Subject format popularity per assignment (grouped bars)
   - A student “habits” table:
     - Mean delta (hours) where delta = `deadline - submission`
     - Number of unique subject formats used and what they are

---

## Files

- `assignments_report.py` — main entry point (prints tables + creates plots)
- `utilities.py` — helper functions:
  - `fetch_text`
  - `parse_readme`
  - `build_subjects_text_from_github_api`
  - `parse_subjects`
  - `add_deadline_deltas`
  - `make_submissions_status_table`
  - `print_per_assignment_summary`
  - `plot_on_time_distributions`
  - `plot_subject_format_popularity`
  - `make_student_habits_table`

---

## Requirements

- Python 3.10+ (uses `zoneinfo`)
- Third-party:
  - `pandas`
  - `matplotlib`
  - `tabulate` (needed for `DataFrame.to_markdown()`)

Install:
```
pip install pandas matplotlib tabulate
```
