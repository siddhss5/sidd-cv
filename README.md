# Siddhartha Srinivasa CV

This repository contains the LaTeX source for Siddhartha Srinivasa's academic CV, including automated data sorting and compilation workflows.

## Quick Start

```bash
# Build the CV (automatically sorts CSV data first)
latexmk -pdf sidd-cv.tex

# Clean auxiliary files
latexmk -c
```

## Features

- **Automated CSV Sorting**: Python script automatically sorts all data files before LaTeX compilation
- **No Manual Sorting**: Removed all `DTLsort` commands from LaTeX files
- **Smart Rebuilding**: `latexmk` only rebuilds when files actually change
- **Full Bibliography Support**: Handles journals, conferences, and miscellaneous publications
- **URL Support**: Clickable links in press coverage section

## File Structure

```
├── sidd-cv.tex              # Main CV document
├── sort_csvs.py             # Python script for sorting CSV files
├── latexmkrc                # latexmk configuration
├── data/                    # CSV data files
│   ├── students-phd.csv     # PhD students
│   ├── students-ms.csv      # MS students  
│   ├── postdocs.csv         # Postdoctoral fellows
│   ├── interns-grad.csv     # Graduate interns
│   ├── interns-undergrad.csv # Undergraduate interns
│   ├── grants.csv           # Research grants
│   └── press.csv            # Press coverage
├── pubs/                    # Bibliography files
│   ├── siddpubs-journal.bib
│   ├── siddpubs-conf.bib
│   └── siddpubs-misc.bib
└── *.tex                    # Section files (mentoring, press, etc.)
```

## Data Management

### CSV Files
All data is stored in CSV files in the `data/` directory. The Python script automatically sorts them according to these rules:

- **`students-phd.csv`**: Sorted by Finish:desc, Start:desc
- **`students-ms.csv`**: Sorted by Finish:desc
- **`postdocs.csv`**: Sorted by Start:desc, Finish:desc
- **`interns-grad.csv`**: Sorted by Year:desc
- **`interns-undergrad.csv`**: Sorted by Finish:desc
- **`grants.csv`**: Sorted by Start:desc, Finish:desc
- **`press.csv`**: Sorted by Year:desc

### Manual Sorting
To sort CSV files manually:
```bash
python3 sort_csvs.py
```

To sort a specific file with custom rules:
```bash
python3 sort_csvs.py data/press.csv Year:desc
python3 sort_csvs.py data/students-phd.csv Finish:desc,Start:desc
```

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
# Sort CSV files first
python3 sort_csvs.py

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
- Automatically runs `python3 sort_csvs.py` before compilation
- Monitors CSV files for changes
- Uses pdflatex as the default engine
- Cleans auxiliary files automatically

### sort_csvs.py
The Python script handles CSV sorting with:
- Default sort configurations for all data files
- Command-line interface for custom sorting
- Robust error handling for missing files
- In-place sorting (replaces original files)

## Dependencies

- **LaTeX**: TeX Live 2025 or later
- **Python 3**: For CSV sorting script
- **latexmk**: For automated compilation
- **datatool**: LaTeX package for CSV processing

## Troubleshooting

### CSV Sorting Issues
If CSV files aren't being sorted:
```bash
# Check if Python script runs
python3 sort_csvs.py

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
1. Add entries to the appropriate CSV file in `data/`
2. Run `latexmk -pdf sidd-cv.tex` to rebuild
3. The Python script will automatically sort the new data

### Modifying Sort Order
Edit the `DEFAULT_SORTS` dictionary in `sort_csvs.py`:
```python
DEFAULT_SORTS = {
    "data/students-phd.csv": [("Finish", "desc"), ("Start", "desc")],
    # Add or modify sort rules here
}
```

## License

This CV template and data are for personal use by Siddhartha Srinivasa.
