# latexmkrc configuration for sidd-cv
# Intelligently sort CSV files only when needed

# Use pdflatex as the default engine
$pdf_mode = 1;

# Clean up auxiliary files
$cleanup_includes_generated = 1;

# Watch for changes in CSV files
$extra_watch_files = "data/*.csv";
