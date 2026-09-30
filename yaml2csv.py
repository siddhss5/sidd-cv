#!/usr/bin/env python3
"""
yaml2csv.py — Convert YAML data from website repo to CSV files for LaTeX CV.

Fetches YAML files (people.yaml, awards.yaml, press.yaml) from the website
repository and generates corresponding CSV files that LaTeX datatool expects.

A paper's awards are not in awards.yaml: they live in the `award` field of the
paper's own BibTeX entry, and awards.yaml holds only awards a person holds, such
as a fellowship or a chair. awards.csv is assembled from both, with the
conference read from the entry's venue so that the award name stays just the
award's name.

Usage:
    python yaml2csv.py --owner siddhss5 --repo siddhss5.github.io --branch main --output-dir data/
"""

import argparse
import csv
import re
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


def read_bib_strings(text: str, prefer_short: bool = False) -> Dict[str, str]:
    """Resolve a .bib file's @string macros.

    These files define every venue twice — "{ACM/IEEE} {HRI}" and "{ACM/IEEE}
    International Conference on Human-Robot Interaction" — and BibTeX uses the
    last definition, which is the full name the website shows. A CV line has no
    room for that, so prefer_short picks each macro's shortest definition
    instead. Shortest rather than first, so reordering the blocks cannot
    silently change the CV.
    """
    definitions: Dict[str, List[str]] = {}
    macros: Dict[str, str] = {}
    for match in re.finditer(r'@string\s*\{\s*(\w+)\s*=\s*(.+?)\}\s*(?=\n)', text, re.S):
        name, raw = match.group(1), match.group(2)
        parts = []
        for piece in raw.split("#"):
            piece = piece.strip()
            if piece.startswith('"') and piece.endswith('"'):
                parts.append(piece[1:-1])
            elif piece in macros:
                parts.append(macros[piece])
            else:
                parts.append(piece.strip('"'))
        macros[name] = "".join(parts)
        definitions.setdefault(name, []).append(macros[name])

    if not prefer_short:
        return macros
    return {name: min(values, key=len) for name, values in definitions.items()}


def strip_braces(value: str) -> str:
    """Drop BibTeX's protective braces: '{ACM/IEEE} Conference' -> 'ACM/IEEE Conference'."""
    return re.sub(r"[{}]", "", value).strip()


def field_value(body: str, name: str, macros: Dict[str, str]) -> str:
    """One field of an entry body, brace-matched, with macros resolved."""
    match = re.search(r"(?:^|,)\s*%s\s*=\s*" % name, body, re.I)
    if not match:
        return ""
    rest = body[match.end():].lstrip()
    if rest.startswith("{"):
        depth, out = 0, []
        for char in rest:
            if char == "{":
                depth += 1
                if depth == 1:
                    continue
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return strip_braces("".join(out))
            out.append(char)
        return strip_braces("".join(out))
    if rest.startswith('"'):
        return strip_braces(rest[1:rest.index('"', 1)])
    token = re.match(r"[\w.-]+", rest)
    if not token:
        return ""
    word = token.group(0)
    return strip_braces(macros.get(word, word))


def split_awards(value: str) -> List[str]:
    """Split an award field on ' and ', with braces protecting an 'and' in a name."""
    parts, depth, current = [], 0, []
    i = 0
    while i < len(value):
        char = value[i]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        if depth == 0 and value[i:i + 5] == " and ":
            parts.append("".join(current))
            current = []
            i += 5
            continue
        current.append(char)
        i += 1
    parts.append("".join(current))
    return [strip_braces(p) for p in parts if strip_braces(p)]


def read_paper_awards(pubs_dir: Path) -> List[Dict[str, str]]:
    """Paper awards from the `award` field of every entry under pubs_dir."""
    rows: List[Dict[str, str]] = []
    bib_files = sorted(pubs_dir.glob("*.bib"))
    if not bib_files:
        print(f"⚠️  No .bib files in {pubs_dir}: no paper awards")
        return rows

    for bib in bib_files:
        text = bib.read_text(encoding="utf-8")
        macros = read_bib_strings(text, prefer_short=True)
        for match in re.finditer(r"@(\w+)\s*\{\s*([^,\n]+),", text):
            if match.group(1).lower() == "string":
                continue
            key = match.group(2).strip()
            depth, end = 1, match.end()
            while end < len(text) and depth:
                if text[end] == "{":
                    depth += 1
                elif text[end] == "}":
                    depth -= 1
                end += 1
            body = text[match.end():end - 1]

            award_field = field_value(body, "award", macros)
            if not award_field:
                continue
            year = field_value(body, "year", macros)
            venue = (field_value(body, "booktitle", macros)
                     or field_value(body, "journal", macros)
                     or field_value(body, "school", macros)
                     or field_value(body, "institution", macros))

            for award in split_awards(award_field):
                award_year = year
                prefix = re.match(r"(\d{4}):\s+(.*)", award)
                if prefix:
                    award_year, award = prefix.group(1), prefix.group(2)
                rows.append({
                    "Award": award,
                    "Conference": venue,
                    "Year": award_year,
                    "Citation": key,
                })

    print(f"✅ Read {len(rows)} paper awards from {len(bib_files)} .bib files")
    return rows


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
    if award.get("pub_link"):
        print(f"⚠️  Award {index} ('{award.get('award', '')}'): has a pub_link, so it "
              "is a paper award — move it to that entry's BibTeX award field")
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
    """Convert awards.yaml — awards a person holds — to awards.csv rows.

    A paper award belongs in that paper's BibTeX `award` field, not here, so one
    that still carries a pub_link is reported and skipped rather than emitted
    twice once the bib also names it.
    """
    rows = []
    for index, award in enumerate(awards_data):
        if award.get("pub_link"):
            print(f"⚠️  Award {index} ('{award.get('award', '')}') has a pub_link: "
                  "it is a paper award and belongs in that entry's BibTeX award "
                  "field. Skipped.")
            continue
        rows.append({
            "Award": award.get("award", ""),
            "Conference": "",
            "Year": str(award.get("year", "")),
            "Citation": "",
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
    parser.add_argument("--pubs-dir", default="pubs", help="Directory of .bib files to read paper awards from")
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

    print("\n🔄 Converting awards...")
    award_rows = convert_awards(awards_data or [])
    award_rows += read_paper_awards(Path(args.pubs_dir))
    if award_rows:
        write_csv(
            award_rows,
            output_dir / "awards.csv",
            ["Award", "Conference", "Year", "Citation"],
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
