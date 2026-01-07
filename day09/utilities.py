import json
import re
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import matplotlib.pyplot as plt

# from __future__ import annotations

def fetch_text(url):
    with urlopen(url) as response:
        return response.read().decode("utf-8")

def build_subjects_text_from_github_api(github_user: str, github_repo: str| None = None) -> str:
    """
    Fetch ALL issues from GitHub (excluding PRs) and return a TSV string that matches subjects.txt format:
        issue_number<TAB>OPEN/CLOSED<TAB>title<TAB><TAB>created_at

    Uses issue.created_at (first submission time), not updated_at.
    """

    def next_link(headers) -> str | None:
        link = headers.get("Link")
        if not link:
            return None
        # Link: <...>; rel="next", <...>; rel="last"
        for part in link.split(","):
            part = part.strip()
            m = re.match(r'<([^>]+)>\s*;\s*rel="([^"]+)"', part)
            if m and m.group(2) == "next":
                return m.group(1)
        return None

    def get_json(url: str):
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "wis-python-course-script",
        }

        req = Request(url, headers=headers)
        with urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data, resp.headers

    base = f"https://api.github.com/repos/{github_user}/{github_repo}/issues"
    params = {"state": "all", "per_page": 100, "page": 1}
    url = base + "?" + urlencode(params)

    lines = []
    while url:
        items, headers = get_json(url)

        for issue in items:
            # The Issues endpoint can include PRs; exclude them
            if "pull_request" in issue:
                continue

            number = issue.get("number")
            state = (issue.get("state") or "").upper()   # OPEN/CLOSED
            title = issue.get("title") or ""
            created_at = issue.get("created_at") or ""

            # Match subjects.txt shape: id \t OPEN/CLOSED \t title \t\t created_at
            lines.append(f"{number}\t{state}\t{title}\t\t{created_at}")

        url = next_link(headers)

    return "\n".join(lines) + ("\n" if lines else "")

# ----------------------------
# 1) Parse README.md
# ----------------------------

def parse_readme(readme_text: str) -> Tuple[List[str], Dict[str, str]]:
    """
    Returns:
      roster: list of student names under '## Students' table
      deadlines: dict { 'Day01': '2025.11.01 22:00', ... } extracted from '* Dead-line: ...'
    """
    lines = readme_text.splitlines()

    roster = _parse_students_table(lines)
    deadlines = _parse_day_deadlines(lines)

    return roster, deadlines


def _parse_students_table(lines: List[str]) -> List[str]:
    # Find the "## Students" section
    start = None
    for i, line in enumerate(lines):
        if re.match(r"^\s*##\s+Students\s*$", line):
            start = i + 1
            break
    if start is None:
        return []

    # End at next ## heading
    end = len(lines)
    for j in range(start, len(lines)):
        if re.match(r"^\s*##\s+\S+", lines[j]):
            end = j
            break

    section = lines[start:end]

    # Collect markdown table lines
    table_lines = [ln for ln in section if ln.strip().startswith("|")]
    if len(table_lines) < 3:
        return []

    # Skip header + separator, parse data rows
    roster = []
    for row in table_lines[2:]:
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if not cells:
            continue

        # In this README, the FIRST cell is like: [Achinoam Shoham](https://...)
        m = re.search(r"\[([^\]]+)\]\(", cells[0])
        if m:
            name = _norm(m.group(1))
            if name:
                roster.append(name)

    # De-duplicate preserving order
    seen = set()
    out = []
    for n in roster:
        k = n.casefold()
        if k not in seen:
            seen.add(k)
            out.append(n)
    return out


def _parse_day_deadlines(lines: List[str]) -> Dict[str, str]:
    """
    Extract deadlines for assignments as ISO like subjects.txt: YYYY-MM-DDTHH:MM:SSZ

    Strategy:
      - Find "### Assignment (day N)" (case-insensitive).
      - Search forward until the NEXT "### Assignment (day ...)" heading (or end of file),
        and within that range take the FIRST occurrence of "Dead-line:".
      - Convert "YYYY.MM.DD HH:MM" into "YYYY-MM-DDTHH:MM:00Z".
      - Strip any "(...)" part.
    """
    assign_hdr = re.compile(
        r"^\s*###\s*Assignment\s*\(\s*day\s*(\d{1,2})\s*\)\s*$", re.IGNORECASE
    )
    deadline_anywhere = re.compile(r"(?i)\bDead-?line:\s*([^\n\r]*)")
    dt = re.compile(r"(\d{4})[.\-/](\d{2})[.\-/](\d{2})\s+(\d{2}):(\d{2})(?::(\d{2}))?")

    def to_iso_z(text: str) -> str:
        text = _norm(text)  # removes "(...)" and normalizes spaces
        m = dt.search(text)
        if not m:
            return text  # fallback: keep cleaned text
        y, mo, d, hh, mm, ss = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5), (m.group(6) or "00")
        return f"{y}-{mo}-{d}T{hh}:{mm}:{ss}Z"

    deadlines: Dict[str, str] = {}

    i = 0
    while i < len(lines):
        m = assign_hdr.match(lines[i])
        if not m:
            i += 1
            continue

        day_num = int(m.group(1))
        key = f"Day{day_num:02d}"

        # Find the boundary: next assignment header
        next_i = i + 1
        while next_i < len(lines) and not assign_hdr.match(lines[next_i]):
            next_i += 1

        # Search only within this day block [i, next_i)
        found = None
        for j in range(i, next_i):
            dm = deadline_anywhere.search(lines[j])
            if dm:
                found = to_iso_z(dm.group(1))
                break

        if found:
            deadlines[key] = found

        i = next_i  # jump to next block (prevents overlap)

    return deadlines


def _norm(s: str) -> str:
    s = re.sub(r"\([^)]*\)", "", s)     # drop "(...)"
    s = re.sub(r"\s+", " ", s).strip()  # normalize whitespace
    return s

# ----------------------------
# 2) Parse day09/subjects.txt
# ----------------------------

def parse_subjects(
    subjects_text: str,
    roster: List[str],
    assignment_names: List[str],
) -> Dict[str, Dict[str, dict]]:
    """
    subjects.txt is TSV:
      issue_id<TAB>OPEN/CLOSED<TAB>title<TAB><TAB>created_at

    Returns nested dict:
      data[student][assignment] = {
          'status': 'OPEN'/'CLOSED',
          'time': '2026-01-03T18:44:38Z',
          'format': '<label>',
          'issue_id': 213
      }
    If multiple issues exist for same (student, assignment), keeps a list under '_all'.
    """
    roster_lookup = _build_roster_lookup(roster)
    assignments_lookup = {a.casefold(): a for a in assignment_names}

    data: Dict[str, Dict[str, dict]] = defaultdict(dict)

    for raw in subjects_text.splitlines():
        if not raw.strip():
            continue

        parts = raw.split("\t")
        if len(parts) < 3:
            continue

        issue_id_str = parts[0].strip()
        status = parts[1].strip().upper()
        title = parts[2].strip()
        created_at = parts[-1].strip()  # last field is the timestamp in this file

        try:
            issue_id = int(issue_id_str)
        except ValueError:
            issue_id = None

        student = _extract_student(title, roster_lookup) or "UNKNOWN"
        assignment = _extract_assignment(title, assignments_lookup) or "UNKNOWN"
        fmt = _classify_subject_format(title)

        entry = {
            "status": status,
            "time": created_at,
            "format": fmt,
            "issue_id": issue_id,
        }

        # If repeated (student, assignment), keep them all
        prev = data[student].get(assignment)
        if prev is None:
            data[student][assignment] = entry
        else:
            all_list = prev.get("_all", [prev])
            all_list.append(entry)
            # keep "latest" as the newest by timestamp string (ISO Z compares lexicographically)
            latest = max(all_list, key=lambda e: e.get("time", ""))
            latest["_all"] = all_list
            data[student][assignment] = latest

    return dict(data)


def _build_roster_lookup(roster: List[str]) -> Dict[str, str]:
    """
    Maps simplified keys -> canonical roster name.
    """
    lookup: Dict[str, str] = {}
    for name in roster:
        lookup[name.casefold()] = name
        lookup[_simplify(name)] = name
    return lookup


def _simplify(s: str) -> str:
    s = s.casefold()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = _norm(s)
    return s


def _extract_student(title: str, roster_lookup: Dict[str, str]) -> Optional[str]:
    """
    Best-effort:
      1) longest roster name substring match (simplified)
      2) parse tail after 'by'
      3) parse tail after '-' (common in this file)
    """
    t_simpl = _simplify(title)

    # Longest match wins
    best = None
    best_len = 0
    for key, canonical in roster_lookup.items():
        if len(key) < 4:
            continue
        if key in t_simpl:
            if len(key) > best_len:
                best = canonical
                best_len = len(key)
    if best:
        return best

    # "by Name"
    m = re.search(r"(?i)\bby\s+(.+?)\s*$", title)
    if m:
        guess = _norm(m.group(1))
        return roster_lookup.get(_simplify(guess)) or guess

    # "... - Name"
    m2 = re.search(r"\s-\s(.+?)\s*$", title)
    if m2:
        guess = _norm(m2.group(1))
        return roster_lookup.get(_simplify(guess)) or guess

    return None


def _extract_assignment(title: str, assignments_lookup: Dict[str, str]) -> Optional[str]:
    t = title.casefold()

    # match known assignment names (prefer longer)
    for k in sorted(assignments_lookup.keys(), key=len, reverse=True):
        if k in t:
            return assignments_lookup[k]

    # fallback: Day## patterns
    m = re.search(r"(?i)\bday\s*[-_ ]*0?(\d{1,2})\b", title)
    if m:
        return f"Day{int(m.group(1)):02d}"

    return None


import re

def _classify_subject_format(title: str) -> str:
    t = title.strip()

    # Helpful quick checks
    has_by = bool(re.search(r"(?i)\bby\b", t))
    has_day = bool(re.search(r"(?i)\bday\s*0?\d{1,2}\b", t))
    has_assignment = bool(re.search(r"(?i)\bassignment\b", t))

    patterns = [
        # Day formats
        (r"(?i)^\s*day\s*0?\d{1,2}\s+by\s+.+$", "Day## by Name"),
        (r"(?i)^\s*day\s*0?\d{1,2}\s*[-–—]\s*.+$", "Day## - Name"),
        (r"(?i)^\s*day\s*0?\d{1,2}\s*:\s*.+$", "Day##: Name"),
        (r"(?i)^\s*day\s*0?\d{1,2}\s+.+$", "Day## Name (no separator)"),

        # Assignment formats
        (r"(?i)^\s*assignment\s*\(?\s*day\s*0?\d{1,2}\s*\)?\s*[-–—:]\s*.+$", "Assignment (day ##): ..."),
        (r"(?i)^\s*assignment\s*0?\d{1,2}\s*[-–—]\s*.+$", "Assignment ## - ..."),
        (r"(?i)^\s*assignment\s*0?\d{1,2}\s+by\s+.+$", "Assignment ## by Name"),
        (r"(?i)^\s*assignment\s*0?\d{1,2}\s*:\s*.+$", "Assignment ##: ..."),

        # Final project common ones
        (r"(?i)^\s*final\s+project\s+proposal\s+by\s+.+$", "Final Project Proposal by Name"),
        (r"(?i)^\s*final\s+project\s+.*$", "Final Project (other)"),

        # Catch-all “contains”
        (r"(?i).*\bday\s*0?\d{1,2}\b.*\bby\b.*", "... Day## ... by ..."),
        (r"(?i).*\bassignment\b.*\bday\s*0?\d{1,2}\b.*", "... Assignment ... day## ..."),
    ]

    for pat, label in patterns:
        if re.match(pat, t):
            return label

    # A slightly-more-informative fallback than plain "Other"
    if has_day and has_by:
        return "Other (mentions Day## + by)"
    if has_day:
        return "Other (mentions Day##)"
    if has_assignment:
        return "Other (mentions Assignment)"
    return "Other"

# ----------------------------
# Helpers
# ----------------------------
def parse_z_iso(ts: str) -> Optional[datetime]:
    if not ts:
        return None
    ts = ts.strip()
    # Handle trailing Z
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(ts).astimezone(timezone.utc)
    except ValueError:
        return None
        
def add_deadline_deltas(
    submissions: Dict[str, Dict[str, dict]],
    deadlines: Dict[str, str],
    *,
    delta_key: str = "delta_to_deadline",
    seconds_key: str = "delta_seconds",
) -> Dict[str, Dict[str, dict]]:
    """
    Compute (submission_time - deadline_time) for each (student, assignment) and add:
      - submissions[student][assignment][delta_key]   -> human string like '-2 days, 03:10:00'
      - submissions[student][assignment][seconds_key] -> signed seconds (negative => early, positive => late)

    Expects:
      - deadlines values like: '2025-11-01T22:00:00Z'
      - submissions[...][...]['time'] like: '2026-01-03T18:44:38Z'

    Modifies submissions in-place and also returns it.
    """

    for student, per_student in submissions.items():
        for assignment, entry in per_student.items():
            # skip the synthetic key used for repeats, if present
            if assignment.startswith("_"):
                continue

            dl_str = deadlines.get(assignment)
            sub_str = entry.get("time", "")

            dl_dt = parse_z_iso(dl_str) if dl_str else None
            sub_dt = parse_z_iso(sub_str)

            if dl_dt is None or sub_dt is None:
                entry[delta_key] = None
                entry[seconds_key] = None
                continue

            delta = sub_dt - dl_dt
            entry[seconds_key] = int(delta.total_seconds())
            entry[delta_key] = str(delta)

            # If you kept multiple submissions in "_all", compute deltas for them too
            if "_all" in entry and isinstance(entry["_all"], list):
                for e in entry["_all"]:
                    sdt = parse_z_iso(e.get("time", ""))
                    if sdt is None:
                        e[delta_key] = None
                        e[seconds_key] = None
                        continue
                    d = sdt - dl_dt
                    e[seconds_key] = int(d.total_seconds())
                    e[delta_key] = str(d)

    return submissions

def make_submissions_status_table(
    roster: List[str],
    assignment_names: List[str],
    submissions: Dict[str, Dict[str, dict]],
    *,
    delta_seconds_key: str = "delta_seconds",
) -> Tuple[List[str], List[List[Any]]]:
    """
    Build a table:
      Rows: one per student in roster
      Columns: Name, one per assignment, Total Late, Total Missing
      Cell values (assignments): 'On-time' / 'Late' / 'Missing'

    Rule:
      - Missing: no submission entry for that (student, assignment)
      - Late: submission[delta_seconds] > 0
      - On-time: submission[delta_seconds] <= 0
        (If delta_seconds missing/None, this function falls back to Missing.)
    """

    def sort_key(a: str):
        # Sort Day01, Day02, ... nicely; otherwise keep at end
        m = re.match(r"(?i)^day(\d{1,2})$", a.strip())
        return (0, int(m.group(1))) if m else (1, a.casefold())

    assignments = sorted(list(assignment_names), key=sort_key)

    header = ["Student"] + assignments + ["Total Late", "Total Missing"]
    rows: List[List[Any]] = []

    for student in roster:
        per_student = submissions.get(student, {})
        row = [student]
        late_count = 0
        missing_count = 0

        for a in assignments:
            entry = per_student.get(a)

            if not entry:
                status = "Missing"
                missing_count += 1
            else:
                ds = entry.get(delta_seconds_key, None)
                if ds is None:
                    status = "Missing"
                    missing_count += 1
                elif ds > 0:
                    status = "Late"
                    late_count += 1
                else:
                    status = "On-time"

            row.append(status)

        row.extend([late_count, missing_count])
        rows.append(row)

    return header, rows

def print_per_assignment_summary(
    roster: List[str],
    assignment_names: List[str],
    submissions: Dict[str, Dict[str, dict]],
    *,
    delta_seconds_key: str = "delta_seconds",
    status_key: str = "status",
) -> None:
    """
    For each assignment, prints:
      Day01: 12 on-time, 3 late, 5 missing (2 unchecked issues)

    Definitions:
      - on-time: has entry and delta_seconds <= 0
      - late: has entry and delta_seconds > 0
      - missing: no entry for that student+assignment OR delta_seconds is None
      - unchecked issues: entry exists but status != 'CLOSED'
    """
    # stable order: as given
    assignment_summary = {}
    for a in assignment_names:
        on_time = late = missing = unchecked = 0

        for student in roster:
            entry = submissions.get(student, {}).get(a)

            if not entry:
                missing += 1
                continue

            ds = entry.get(delta_seconds_key, None)
            if ds is None:
                missing += 1
            elif ds > 0:
                late += 1
            else:
                on_time += 1

            if (entry.get(status_key) or "").upper() != "CLOSED":
                unchecked += 1

        assignment_summary[a] = (on_time, late, missing, unchecked)
    
    return assignment_summary

def _parse_iso_z(ts: str) -> datetime | None:
    if not ts:
        return None
    ts = ts.strip()
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(ts).astimezone(timezone.utc)
    except ValueError:
        return None

def plot_on_time_distributions(
    submissions: dict,
    *,
    delta_seconds_key: str = "delta_seconds",
    time_key: str = "time",
    tz_name: str = "Asia/Jerusalem",
) -> None:
    """
    Makes two bar plots using ONLY on-time submissions (delta_seconds <= 0):
      A) Count by weekday
      B) Count by hour (0..23)
    """
    tz = ZoneInfo(tz_name)

    weekday_counts = Counter()
    hour_counts = Counter()

    for _student, per_student in submissions.items():
        for _assignment, entry in per_student.items():
            if not isinstance(entry, dict):
                continue
            if _assignment.startswith("_"):
                continue

            ds = entry.get(delta_seconds_key, None)
            if ds is None or ds > 0:
                continue  # only on-time

            dt_utc = _parse_iso_z(entry.get(time_key, ""))
            if dt_utc is None:
                continue
            dt_local = dt_utc.astimezone(tz)

            weekday_counts[dt_local.weekday()] += 1  # Mon=0..Sun=6
            hour_counts[dt_local.hour] += 1

    # ---- Plot A: weekday ----
    # Want Sunday..Saturday
    weekday_order = [6, 0, 1, 2, 3, 4, 5]
    weekday_labels = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    weekday_values = [weekday_counts[i] for i in weekday_order]

    plt.figure(figsize=(9, 4))
    plt.bar(weekday_labels, weekday_values)
    plt.title("On-time submissions by weekday")
    plt.ylabel("Count")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.show()

    # ---- Plot B: hour ----
    hour_labels = [f"{h:02d}:00-{h:02d}:59" for h in range(24)]
    hour_values = [hour_counts[h] for h in range(24)]

    plt.figure(figsize=(12, 4))
    plt.bar(hour_labels, hour_values)
    plt.title("On-time submissions by hour of day")
    plt.ylabel("Count")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()


def plot_subject_format_popularity(
    submissions: dict,
    assignment_names: list[str],
    *,
    format_key: str = "format",
) -> None:
    """
    Grouped bar plot:
      x-axis: assignments
      bars per x: subject formats used for that assignment
      y-axis: counts
      legend: outside, below plot
    Counts every issue:
      - if entry has "_all": counts each item in that list
      - else counts the single entry
    """
    # counts[assignment][format] = count
    counts = defaultdict(Counter)

    for _student, per_student in submissions.items():
        for assignment, entry in per_student.items():
            if assignment not in assignment_names:
                continue
            if not isinstance(entry, dict):
                continue

            entries = entry.get("_all") if isinstance(entry.get("_all"), list) else [entry]
            for e in entries:
                fmt = (e.get(format_key) or "Other").strip() or "Other"
                counts[assignment][fmt] += 1

    # Collect formats that appear anywhere (stable-ish order: most common overall first)
    overall = Counter()
    for a in assignment_names:
        overall.update(counts[a])

    formats = [fmt for fmt, _ in overall.most_common()]
    if not formats:
        print("No subject formats found to plot.")
        return

    # Build matrix format x assignment
    matrix = [[counts[a].get(fmt, 0) for a in assignment_names] for fmt in formats]

    x = list(range(len(assignment_names)))
    n_fmt = len(formats)
    width = 0.8 / n_fmt

    plt.figure(figsize=(max(10, len(assignment_names) * 0.6), 5))
    ax = plt.gca()

    # Center the grouped bars around each integer x
    for k, fmt in enumerate(formats):
        offset = (k - (n_fmt - 1) / 2) * width
        ax.bar([xi + offset for xi in x], matrix[k], width=width, label=fmt)

    ax.set_title("Subject format popularity by assignment")
    ax.set_ylabel("Count")
    ax.set_xticks(x)
    ax.set_xticklabels(assignment_names, rotation=30, ha="right")

    # Legend outside below
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.20),
        ncol=min(n_fmt, 4),
        frameon=False,
    )

    plt.tight_layout()
    plt.show()

def make_student_habits_table(
    roster: List[str],
    submissions: Dict[str, Dict[str, dict]],
    *,
    delta_seconds_key: str = "delta_seconds",
    format_key: str = "format",
) -> Tuple[List[str], List[List[Any]]]:
    """
    Builds a per-student habits table.

    Columns:
      - Student
      - Mean delta (hours), where delta = deadline - submission = -(submission - deadline)
      - # unique subject formats used

    Notes:
      - Uses only entries that have delta_seconds (ignores Missing / None).
      - If an entry contains "_all" (multiple issues), each one is included.
      - Std is population std (divide by N). Change to (N-1) if you want sample std.
    """
    header = ["Student", "Avg. sub. time (hours)", "Unique formats", "Formats"]
    rows: List[List[Any]] = []

    for student in roster:
        per_student = submissions.get(student, {})

        deltas_hours: List[float] = []
        formats = set()

        for _assignment, entry in per_student.items():
            if not isinstance(entry, dict) or _assignment.startswith("_"):
                continue

            entries = entry.get("_all") if isinstance(entry.get("_all"), list) else [entry]

            for e in entries:
                ds = e.get(delta_seconds_key, None)
                if ds is None:
                    continue

                # user wants: deadline - submission, but ds is (submission - deadline)
                delta_deadline_minus_sub = (-ds) / 3600.0
                deltas_hours.append(delta_deadline_minus_sub)

                fmt = (e.get(format_key) or "").strip()
                if fmt:
                    formats.add(fmt)

        if deltas_hours:
            mean = sum(deltas_hours) / len(deltas_hours)
            mean_out = round(mean, 2)
        else:
            mean_out = None

        rows.append([student, mean_out, len(formats), formats])

    return header, rows
