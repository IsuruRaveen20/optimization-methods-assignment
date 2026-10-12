"""List placeholders that must be replaced before uploading Optimization-assignment.zip.

Author: sharmilak99 <sharmilakavi822@gmail.com>
Created: 2026-10-12
"""
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
problems = []
for name in ("members.txt", "submission.txt"):
    for n, line in enumerate((ROOT / name).read_text(encoding="utf-8").splitlines(), 1):
        if re.search(r"\[(Enter|PASTE|TODO)[^\]]*\]", line, re.I) or "FULL NAME" in line:
            problems.append(f"{name}:{n}: {line.strip()}")
if not (ROOT / ".git").exists():
    problems.append("no .git directory - create the repository and push it to GitHub")
else:
    log = subprocess.run(["git", "log", "--oneline"], cwd=ROOT, capture_output=True, text=True).stdout.splitlines()
    problems += [] if len(log) >= 10 else [f"only {len(log)} commits in history"]
    allowed = {"IsuruRaveen20", "sharmilak99"}
    authors = subprocess.run(
        ["git", "log", "--format=%an"], cwd=ROOT, capture_output=True, text=True
    ).stdout.splitlines()
    bad = sorted({a for a in authors if a not in allowed})
    if bad:
        problems.append(f"unexpected commit author(s): {', '.join(bad)}")
    status = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    if status:
        problems.append("uncommitted changes:\n" + status)

pdf = subprocess.run(["pdftotext", str(ROOT / "docs/final_report.pdf"), "-"], capture_output=True, text=True).stdout
if "fill in" in pdf:
    problems.append("final_report.pdf still contains placeholders - fill members.txt/submission.txt, run docs/build_report.py")
if problems:
    print("NOT READY:")
    print("\n".join(" - " + p for p in problems))
    sys.exit(1)
print("All checks passed.")
