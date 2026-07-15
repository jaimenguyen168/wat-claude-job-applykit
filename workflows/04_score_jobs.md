# Workflow 04 — Score Jobs

## Objective

Evaluate each deduplicated job against the candidate profile. Score 0–100, apply hard rejection rules, assign a verdict (yes/no), and persist results back to today's jobs file.

## When to Run

After Workflow 02 (deduplicate). Only runs Mon–Thu.

## Required Inputs

- `.data/jobs_YYYY-MM-DD.json` — deduplicated jobs from today
- `.data/candidate_profile.json` — candidate profile (optional but recommended)

## Steps

### Step 1 — Prepare scoring context

Run:
```
.venv/bin/python tools/score_jobs.py
```

This prints the candidate profile, scoring rules, and all unscored jobs formatted for the agent to evaluate.

### Step 2 — Agent scores each job

Read the output carefully. For every job, apply the rules below and produce a JSON array:

```json
[
  {"id": "123456", "score": 82, "verdict": "yes", "reason": "Strong React/Next.js match, remote-friendly, NYC-based"},
  {"id": "789012", "score": 30, "verdict": "no",  "reason": "Requires 3 years experience, C++/Java only stack"}
]
```

#### Scoring Rules

**HARD REJECTIONS — score 0, verdict: no immediately:**
- Job requires 2+ years of experience
- Tech stack lists only technologies the candidate does not have (e.g. C, C++, Ruby on Rails, Angular, .NET, Java, Go, Rust) — if that's the entire requirement, not just one mention
- Location is in: Florida, Mississippi, Tennessee, Arkansas, Idaho, Oklahoma, Missouri, West Virginia, Indiana — **unless explicitly 100% remote**

**BASE SCORE — start at 50, adjust up/down:**

| Signal | Points |
|--------|--------|
| Strong skill overlap (3+ matching skills) | +15 to +20 |
| Moderate skill overlap (1–2 matching skills) | +5 to +10 |
| No skill overlap | -20 |
| Entry-level / 0–1 year exp | +10 |
| Remote work | +10 |
| Located in Philadelphia, New York, Baltimore, New Jersey | +10 |
| Located in California | +8 |
| Role title matches candidate's focus (frontend, mobile, fullstack) | +10 |
| High applicant count (500+) | -5 |
| Salary listed and competitive | +5 |

**Verdict threshold: score ≥ 75 → yes, else no**

### Step 3 — Save verdicts

Pass the JSON array to the save tool:

```
echo '<JSON_ARRAY>' | .venv/bin/python tools/save_scored_jobs.py
```

Or write it to a temp file first:
```
.venv/bin/python tools/save_scored_jobs.py /path/to/scores.json
```

The tool merges `score`, `verdict`, and `reason` back into each job object in today's jobs file.

## Edge Cases

- **No jobs file:** `score_jobs.py` exits with error — run Workflows 01 and 02 first.
- **Profile missing:** Scoring continues with job content only — a warning is printed.
- **All jobs already scored:** `score_jobs.py` exits cleanly with nothing to do.
- **Mixed scored/unscored:** Only unscored jobs are included in the context.

## Output

`.data/jobs_YYYY-MM-DD.json` — each job now includes:
```json
{
  "score": 82,
  "verdict": "yes",
  "reason": "..."
}
```

## Files Involved

| File | Purpose |
|------|---------|
| `tools/score_jobs.py` | Formats jobs + profile for agent scoring |
| `tools/save_scored_jobs.py` | Merges agent verdicts back into jobs file |
| `.data/jobs_YYYY-MM-DD.json` | Updated with score, verdict, reason per job |
| `.data/candidate_profile.json` | Candidate context for scoring |

## Next

Run **Workflow 05 — [Next Stage]**
