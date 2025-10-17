# latexmkrc configuration for sidd-cv
# Automatically sort CSV files before LaTeX compilation

# Use pdflatex as the default engine
$pdf_mode = 1;

# Clean up auxiliary files
$cleanup_includes_generated = 1;

# Watch for changes in CSV files
$extra_watch_files = "data/*.csv";

# Force rebuild if CSV files change
$force_mode = 1;

# Custom build sequence: sort CSV files first, then compile
$pdflatex = "python3 sort_csvs.py && pdflatex %O %S";
