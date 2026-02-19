#!/usr/bin/env python3
"""
yaml2csv.py — Convert YAML data from website repo to CSV files for LaTeX CV.

Fetches YAML files (people.yaml, awards.yaml, press.yaml) from the website
repository and generates corresponding CSV files that LaTeX datatool expects.

Usage:
    python yaml2csv.py --owner siddhss5 --repo siddhss5.github.io --branch main --output-dir data/
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install pyyaml")
    sys.exit(1)


# Sort specifications matching sort_csvs.py
SORT_SPECS = {
    "students-phd.csv": [("Finish", "desc"), ("Start", "desc")],
    "students-ms.csv": [("Finish", "desc")],
    "postdocs.csv": [("Start", "desc"), ("Finish", "desc")],
    "interns-grad.csv": [("Year", "desc")],
    "interns-undergrad.csv": [("Finish", "desc")],
    "awards.csv": [("Year", "desc")],
    "press.csv": [("Year", "desc")],
}


def fetch_yaml(owner: str, repo: str, branch: str, file_path: str) -> Any:
    """Fetch YAML file from GitHub repository."""
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}"
    try:
        with urlopen(url) as response:
            return yaml.safe_load(response.read())
    except HTTPError as e:
        if e.code == 404:
            print(f"❌ {file_path} not found in {owner}/{repo}/{branch}")
            print(f"   Check: https://github.com/{owner}/{repo}/blob/{branch}/{file_path}")
            return None
        raise
    except URLError as e:
        print(f"❌ Error fetching {file_path}: {e}")
        print(f"   URL: {url}")
        raise


def extract_bibtex_key(pub_link: str) -> str:
    """Extract BibTeX key from publication link."""
    if not pub_link:
        return ""
    # Strip /publications/# prefix
    return pub_link.replace("/publications/#", "").replace("/publications/", "")


def validate_person(person: Dict, index: int) -> bool:
    """Validate person data structure."""
    required = ["name", "role"]
    missing = [f for f in required if not person.get(f)]
    if missing:
        print(f"⚠️  Person {index}: Missing required fields: {missing}")
        return False
    return True


def validate_award(award: Dict, index: int) -> bool:
    """Validate award data structure."""
    required = ["award", "year"]
    missing = [f for f in required if not award.get(f)]
    if missing:
        print(f"⚠️  Award {index}: Missing required fields: {missing}")
        return False
    return True


def validate_press_item(item: Dict, index: int) -> bool:
    """Validate press item data structure."""
    required = ["Title", "Source", "Year"]
    missing = [f for f in required if not item.get(f)]
    if missing:
        print(f"⚠️  Press item {index}: Missing required fields: {missing}")
        return False
    return True


def validate_yaml_data(people_data: List[Dict], awards_data: List[Dict], press_data: List[Dict]) -> bool:
    """Validate all YAML data structures."""
    valid = True

    if people_data:
        print("\n🔍 Validating people.yaml...")
        for i, person in enumerate(people_data):
            if not validate_person(person, i):
                valid = False
        print(f"✅ Validated {len(people_data)} people entries")

    if awards_data:
        print("\n🔍 Validating awards.yaml...")
        for i, award in enumerate(awards_data):
            if not validate_award(award, i):
                valid = False
        print(f"✅ Validated {len(awards_data)} award entries")

    if press_data:
        print("\n🔍 Validating press.yaml...")
        for i, item in enumerate(press_data):
            if not validate_press_item(item, i):
                valid = False
        print(f"✅ Validated {len(press_data)} press entries")

    return valid


def sort_rows(rows: List[Dict[str, str]], sort_spec: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    """Sort rows according to specification (replicates sort_csvs.py logic)."""
    if not rows or not sort_spec:
        return rows

    def sort_key(row: Dict[str, str]) -> Tuple:
        result = []
        for key, order in sort_spec:
            val = row.get(key, "").strip()
            # Empty fields sort to "0000" if desc, "zzzz" if asc
            val = val or ("0000" if order == "desc" else "zzzz")
            result.append(val)
        return tuple(result)

    # Reverse if first column is descending
    reverse = sort_spec and sort_spec[0][1] == "desc"
    return sorted(rows, key=sort_key, reverse=reverse)


def write_csv(rows: List[Dict[str, str]], output_path: Path, fieldnames: List[str], sort_spec: List[Tuple[str, str]]):
    """Write sorted CSV file."""
    if not rows:
        print(f"⚠️  No data to write to {output_path.name}, skipping")
        return

    # Sort rows
    sorted_rows = sort_rows(rows, sort_spec)

    # Write CSV
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sorted_rows)

    print(f"✅ Generated {output_path.name} ({len(sorted_rows)} rows)")


def convert_people_to_students_phd(people_data: List[Dict]) -> List[Dict[str, str]]:
    """Convert people.yaml (role=phd_student) to students-phd.csv format."""
    rows = []
    for person in people_data:
        if person.get("role") != "phd_student":
            continue

        rows.append({
            "Name": person.get("name", ""),
            "Coadvisor": person.get("co_advisor", ""),
            "Title": person.get("thesis_title", ""),
            "Start": str(person.get("start_year", "")),
            "Finish": str(person.get("end_year", "")) if person.get("end_year") else "",
            "NowAt": person.get("current_position", ""),
        })

    return rows


def convert_people_to_students_ms(people_data: List[Dict]) -> List[Dict[str, str]]:
    """Convert people.yaml (role=ms_student) to students-ms.csv format."""
    rows = []
    for person in people_data:
        if person.get("role") != "ms_student":
            continue

        rows.append({
            "Name": person.get("name", ""),
            "Coadvisor": person.get("co_advisor", ""),
            "Title": person.get("thesis_title", ""),
            "Start": str(person.get("start_year", "")),
            "Finish": str(person.get("end_year", "")) if person.get("end_year") else "",
            "NowAt": person.get("current_position", ""),
        })

    return rows


def convert_people_to_postdocs(people_data: List[Dict]) -> List[Dict[str, str]]:
    """Convert people.yaml (role=postdoc) to postdocs.csv format."""
    rows = []
    for person in people_data:
        if person.get("role") != "postdoc":
            continue

        rows.append({
            "Name": person.get("name", ""),
            "Coadvisor": person.get("co_advisor", ""),
            "Start": str(person.get("start_year", "")),
            "Finish": str(person.get("end_year", "")) if person.get("end_year") else "",
            "NowAt": person.get("current_position", ""),
        })

    return rows


def convert_people_to_interns_grad(people_data: List[Dict]) -> List[Dict[str, str]]:
    """Convert people.yaml (role=intern_grad) to interns-grad.csv format."""
    rows = []
    for person in people_data:
        if person.get("role") != "intern_grad":
            continue

        rows.append({
            "Name": person.get("name", ""),
            "From": person.get("university", ""),
            "Year": str(person.get("start_year", "")),
        })

    return rows


def convert_people_to_interns_undergrad(people_data: List[Dict]) -> List[Dict[str, str]]:
    """Convert people.yaml (role=intern_undergrad) to interns-undergrad.csv format."""
    rows = []
    for person in people_data:
        if person.get("role") != "intern_undergrad":
            continue

        rows.append({
            "Name": person.get("name", ""),
            "From": person.get("university", ""),
            "Start": str(person.get("start_year", "")),
            "Finish": str(person.get("end_year", "")) if person.get("end_year") else "",
        })

    return rows


def convert_awards(awards_data: List[Dict]) -> List[Dict[str, str]]:
    """Convert awards.yaml to awards.csv format."""
    rows = []
    for award in awards_data:
        # Extract BibTeX key from pub_link
        citation = extract_bibtex_key(award.get("pub_link", ""))

        rows.append({
            "Award": award.get("award", ""),
            "Year": str(award.get("year", "")),
            "Citation": citation,
        })

    return rows


def convert_press(press_data: List[Dict]) -> List[Dict[str, str]]:
    """Convert press.yaml to press.csv format (fields already match!)."""
    rows = []
    for item in press_data:
        rows.append({
            "Title": item.get("Title", ""),
            "Source": item.get("Source", ""),
            "Year": str(item.get("Year", "")),
            "Link": item.get("Link", ""),
        })

    return rows


def main():
    parser = argparse.ArgumentParser(
        description="Convert YAML data from website repo to CSV files for LaTeX CV"
    )
    parser.add_argument("--owner", default="siddhss5", help="GitHub repository owner")
    parser.add_argument("--repo", default="siddhss5.github.io", help="GitHub repository name")
    parser.add_argument("--branch", default="main", help="Git branch to fetch from")
    parser.add_argument("--output-dir", default="data", help="Output directory for CSV files")
    parser.add_argument("--validate", action="store_true", help="Validate YAML structure without writing CSV files")

    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    print(f"📥 Fetching YAML files from {args.owner}/{args.repo} ({args.branch} branch)...\n")

    # Fetch YAML files
    people_data = fetch_yaml(args.owner, args.repo, args.branch, "data/people.yaml")
    awards_data = fetch_yaml(args.owner, args.repo, args.branch, "data/awards.yaml")
    press_data = fetch_yaml(args.owner, args.repo, args.branch, "data/press.yaml")

    # If validate-only mode, run validation and exit
    if args.validate:
        print("\n" + "="*50)
        print("VALIDATION MODE")
        print("="*50)
        valid = validate_yaml_data(people_data or [], awards_data or [], press_data or [])
        if valid:
            print("\n✅ All YAML data is valid!")
            sys.exit(0)
        else:
            print("\n❌ Validation failed - fix errors above")
            sys.exit(1)

    # Convert and write CSV files
    if people_data:
        print("🔄 Converting people.yaml...")

        # PhD students
        phd_rows = convert_people_to_students_phd(people_data)
        write_csv(
            phd_rows,
            output_dir / "students-phd.csv",
            ["Name", "Coadvisor", "Title", "Start", "Finish", "NowAt"],
            SORT_SPECS["students-phd.csv"],
        )

        # MS students
        ms_rows = convert_people_to_students_ms(people_data)
        write_csv(
            ms_rows,
            output_dir / "students-ms.csv",
            ["Name", "Coadvisor", "Title", "Start", "Finish", "NowAt"],
            SORT_SPECS["students-ms.csv"],
        )

        # Postdocs
        postdoc_rows = convert_people_to_postdocs(people_data)
        write_csv(
            postdoc_rows,
            output_dir / "postdocs.csv",
            ["Name", "Coadvisor", "Start", "Finish", "NowAt"],
            SORT_SPECS["postdocs.csv"],
        )

        # Graduate interns
        intern_grad_rows = convert_people_to_interns_grad(people_data)
        if intern_grad_rows:
            write_csv(
                intern_grad_rows,
                output_dir / "interns-grad.csv",
                ["Name", "From", "Year"],
                SORT_SPECS["interns-grad.csv"],
            )
        else:
            print("⚠️  No graduate intern data found in people.yaml")

        # Undergraduate interns
        intern_undergrad_rows = convert_people_to_interns_undergrad(people_data)
        if intern_undergrad_rows:
            write_csv(
                intern_undergrad_rows,
                output_dir / "interns-undergrad.csv",
                ["Name", "From", "Start", "Finish"],
                SORT_SPECS["interns-undergrad.csv"],
            )
        else:
            print("⚠️  No undergraduate intern data found in people.yaml")

    if awards_data:
        print("\n🔄 Converting awards.yaml...")
        award_rows = convert_awards(awards_data)
        write_csv(
            award_rows,
            output_dir / "awards.csv",
            ["Award", "Year", "Citation"],
            SORT_SPECS["awards.csv"],
        )

    if press_data:
        print("\n🔄 Converting press.yaml...")
        press_rows = convert_press(press_data)
        write_csv(
            press_rows,
            output_dir / "press.csv",
            ["Title", "Source", "Year", "Link"],
            SORT_SPECS["press.csv"],
        )

    print("\n✨ CSV generation complete!")
    print("📝 Note: grants.csv remains hand-edited (not generated from YAML)")


if __name__ == "__main__":
    main()
