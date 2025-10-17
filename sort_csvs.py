#!/usr/bin/env python3
"""
sort_csvs.py — sort PRL CV data files consistently before LaTeX build.

Usage:
    python3 sort_csvs.py
or
    python3 sort_csvs.py data/students-phd.csv Finish:desc,Start:desc
    python3 sort_csvs.py data/press.csv Year:desc
"""

import csv, sys, pathlib

# ---------------------------------------------------------------------
# Default sort configuration for all data files
# ---------------------------------------------------------------------
DEFAULT_SORTS = {
    "data/students-phd.csv": [("Finish", "desc"), ("Start", "desc")],
    "data/students-ms.csv": [("Finish", "desc")],
    "data/postdocs.csv": [("Start", "desc"), ("Finish", "desc")],
    "data/interns-grad.csv": [("Year", "desc")],
    "data/interns-undergrad.csv": [("Finish", "desc")],
    "data/grants.csv": [("Start", "desc"), ("Finish", "desc")],
    "data/press.csv": [("Year", "desc")],
}

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def parse_sort_spec(spec_str):
    """Parse a command-line column specification like 'Year:desc,Name:asc'."""
    specs = []
    for pair in spec_str.split(","):
        if not pair.strip():
            continue
        parts = pair.split(":")
        key = parts[0]
        order = parts[1] if len(parts) > 1 else "asc"
        specs.append((key, order))
    return specs


def sort_csv(path, sort_keys):
    path = pathlib.Path(path)
    if not path.exists():
        print(f"⚠️  {path} not found, skipping.")
        return

    rows = list(csv.DictReader(open(path, newline="")))
    if not rows:
        print(f"⚠️  {path} empty or malformed, skipping.")
        return

    def sort_key(row):
        result = []
        for key, order in sort_keys:
            val = row.get(key, "")
            # Normalize for consistent ordering
            val = val.strip()
            # Empty fields sort last if descending
            val = val or ("0000" if order == "desc" else "zzzz")
            result.append(val)
        return tuple(result)

    # Reverse sort if any key is descending
    reverse = sort_keys and sort_keys[0][1] == "desc"
    rows.sort(key=sort_key, reverse=reverse)

    # Write back to the same file
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Sorted {path}")


def main():
    if len(sys.argv) == 1:
        # Run defaults
        for file, specs in DEFAULT_SORTS.items():
            sort_csv(file, specs)
    elif len(sys.argv) == 3:
        file = sys.argv[1]
        specs = parse_sort_spec(sys.argv[2])
        sort_csv(file, specs)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
