# Siddhartha Srinivasa CV

This repository contains the LaTeX source for Siddhartha Srinivasa's academic CV with automated YAML-to-CSV conversion and cross-repository build triggers.

## Quick Start

```bash
# Generate CSV files from YAML data (from website repo)
python3 yaml2csv.py --owner siddhss5 --repo siddhss5.github.io --branch main --output-dir data/

# Build the CV
latexmk -pdf sidd-cv.tex

# Clean auxiliary files
latexmk -c
```

## Features

- **YAML Source of Truth**: Data sourced from [website repo](https://github.com/siddhss5/siddhss5.github.io) YAML files
- **Automated CSV Generation**: Python script fetches YAML and generates sorted CSV files
- **Cross-Repo Automation**: CV automatically rebuilds when YAML files change in website repo
- **Smart Sorting**: Built-in sorting eliminates need for manual data ordering
- **Full Bibliography Support**: Handles journals, conferences, and miscellaneous publications
- **URL Support**: Clickable links in press coverage section

## File Structure

```
├── sidd-cv.tex              # Main CV document
├── yaml2csv.py              # Script to convert YAML → CSV
├── latexmkrc                # latexmk configuration
├── data/                    # CSV data files (generated from YAML)
│   ├── students-phd.csv     # PhD students (generated)
│   ├── students-ms.csv      # MS students (generated)
│   ├── postdocs.csv         # Postdoctoral fellows (generated)
│   ├── interns-grad.csv     # Graduate interns (generated)
│   ├── interns-undergrad.csv # Undergraduate interns (generated)
│   ├── grants.csv           # Research grants (hand-edited)
│   ├── awards.csv           # Awards (generated)
│   └── press.csv            # Press coverage (generated)
├── pubs/                    # Bibliography files
│   ├── siddpubs-journal.bib
│   ├── siddpubs-conf.bib
│   └── siddpubs-misc.bib
└── *.tex                    # Section files (mentoring, press, etc.)
```

## Data Management

### YAML Source of Truth
Most CV data is maintained in YAML files in the [website repository](https://github.com/siddhss5/siddhss5.github.io):
- `data/people.yaml` - PhD students, MS students, postdocs, interns
- `data/awards.yaml` - Awards and honors
- `data/press.yaml` - Press coverage

**Exception**: `data/grants.csv` remains hand-edited in this repository.

### Generating CSV Files
Run `yaml2csv.py` to fetch YAML from the website repo and generate CSV files:

```bash
python3 yaml2csv.py --owner siddhss5 --repo siddhss5.github.io --branch main --output-dir data/
```

The script automatically:
- Fetches latest YAML data from website repo
- Converts YAML to CSV format that LaTeX datatool expects
- Applies proper sorting (e.g., PhD students by Finish:desc, Start:desc)
- Handles current vs. alumni distinctions (empty end_year fields)

### Automated Updates
The CV automatically rebuilds when YAML files change in the website repo via GitHub Actions `repository_dispatch`. No manual intervention needed!

## Compilation

### Using latexmk (Recommended)
```bash
# Build the CV
latexmk -pdf sidd-cv.tex

# Force rebuild (useful when CSV files change)
latexmk -pdf -g sidd-cv.tex

# Clean auxiliary files
latexmk -c
```

### Manual Compilation
```bash
# Generate CSV files from YAML first
python3 yaml2csv.py --owner siddhss5 --repo siddhss5.github.io --branch main --output-dir data/

# Compile LaTeX
pdflatex sidd-cv.tex
bibtex jour
bibtex conf
bibtex misc
pdflatex sidd-cv.tex
pdflatex sidd-cv.tex
```

## Configuration

### latexmkrc
The `latexmkrc` file configures the build process:
- Monitors CSV files for changes
- Uses pdflatex as the default engine
- Cleans auxiliary files automatically

### yaml2csv.py
The Python script handles YAML-to-CSV conversion:
- Fetches YAML files from website repo via GitHub API
- Maps YAML fields to CSV columns (e.g., `co_advisor` → `Coadvisor`)
- Applies sorting rules for each data type
- Handles empty fields correctly (e.g., current students have no end_year)
- Gracefully handles missing data (e.g., interns not yet in YAML)

## Dependencies

- **LaTeX**: TeX Live 2025 or later
- **Python 3.9+**: For yaml2csv.py script
- **PyYAML**: Install with `pip install pyyaml`
- **latexmk**: For automated compilation
- **datatool**: LaTeX package for CSV processing

## Troubleshooting

### CSV Generation Issues
If CSV files aren't being generated:
```bash
# Check if yaml2csv.py runs
python3 yaml2csv.py --owner siddhss5 --repo siddhss5.github.io --branch main --output-dir data/

# Verify PyYAML is installed
pip install pyyaml

# Force rebuild with latexmk
latexmk -pdf -g sidd-cv.tex
```

### LaTeX Compilation Issues
If compilation fails:
```bash
# Clean all auxiliary files
latexmk -c

# Check for missing dependencies
tlmgr install datatool
```

### Bibliography Issues
If references aren't resolved:
```bash
# Force bibliography rebuild
latexmk -pdf -g sidd-cv.tex
```

## Development

### Adding New Data
1. **For people, awards, press**: Edit YAML files in the [website repo](https://github.com/siddhss5/siddhss5.github.io)
   - Push changes to trigger automatic CV rebuild via repository_dispatch
2. **For grants**: Edit `data/grants.csv` directly in this repo (hand-edited)
3. Run `latexmk -pdf sidd-cv.tex` to rebuild locally

### Modifying Sort Order
Edit the `SORT_SPECS` dictionary in `yaml2csv.py`:
```python
SORT_SPECS = {
    "students-phd.csv": [("Finish", "desc"), ("Start", "desc")],
    # Add or modify sort rules here
}
```

## Local Development

### Python Environment Setup

For development, it's recommended to use a virtual environment:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or: venv\Scripts\activate  # On Windows

# Install dependencies
pip install pyyaml
```

### Testing Changes Locally

Before committing, test your changes:

```bash
# 1. Update CSV files from YAML
python3 yaml2csv.py --owner siddhss5 --repo siddhss5.github.io --branch main --output-dir data/

# 2. Compile the CV
latexmk -pdf sidd-cv.tex

# 3. Verify the PDF output
open sidd-cv.pdf  # macOS
# or: xdg-open sidd-cv.pdf  # Linux
```

### Managing Publications

The `pubs/` directory contains BibTeX files for different publication types:

- `siddpubs-journal.bib` - Journal papers
- `siddpubs-conf.bib` - Conference papers
- `siddpubs-misc.bib` - Technical reports, theses

**To update publications:**

1. Edit the appropriate `.bib` file directly
2. Run `latexmk -pdf sidd-cv.tex` to rebuild the CV
3. Verify the changes in the generated PDF
4. Commit both the `.bib` changes and the regenerated `sidd-cv.pdf`

**Note**: The `pubs/` directory is tracked directly in this repository (not a submodule).

## Troubleshooting

### "Missing CSV file" errors

If LaTeX compilation fails with missing CSV errors:

```bash
# Regenerate all CSV files from YAML
python3 yaml2csv.py --owner siddhss5 --repo siddhss5.github.io --branch main --output-dir data/

# Force rebuild
latexmk -pdf -g sidd-cv.tex
```

### "PyYAML not found" error

```bash
pip install pyyaml

# If using system Python on macOS:
python3 -m pip install --user pyyaml
```

### Bibliography not updating

If publication changes aren't reflected:

```bash
# Clean all auxiliary files
latexmk -c

# Remove bibliography cache
rm *.bbl *.blg *.aux

# Force full rebuild
latexmk -pdf -g sidd-cv.tex
```

### GitHub Actions build failing

1. Check the [Actions tab](../../actions) for detailed error logs
2. Verify YAML files are valid in the website repo
3. Ensure `CV_REPO_PAT` secret is configured in website repo (for cross-repo triggers)
4. Test locally with the same commands as CI uses

## GitHub Actions

This repository includes automated PDF building via GitHub Actions:

### Automatic Builds
- **Triggers**:
  - Push to `main` branch
  - Pull requests
  - Repository dispatch from website repo (when YAML files change)
  - Manual workflow dispatch
- **Actions**:
  - Fetches YAML files from website repo
  - Converts YAML to CSV using yaml2csv.py
  - Compiles PDF using latexmk
  - Commits updated PDF back to repo

### Cross-Repository Automation
When YAML files are updated in the website repo:
1. Website repo workflow sends `repository_dispatch` event
2. CV repo workflow triggers automatically
3. Fresh CSV files are generated from latest YAML
4. PDF is rebuilt and committed

### Workflow Files
- `.github/workflows/build.yml` - CV build workflow (this repo)
- `.github/workflows/trigger-cv-build.yml` - Trigger workflow (website repo)

### Setup Requirements
The website repo needs a `CV_REPO_PAT` secret (Personal Access Token) with `repo` scope to trigger builds in this repo.

## License

This CV template and data are for personal use by Siddhartha Srinivasa.
