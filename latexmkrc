# latexmkrc configuration for sidd-cv
# Intelligently sort CSV files only when needed

# Use pdflatex as the default engine
$pdf_mode = 1;

# Clean up auxiliary files
$cleanup_includes_generated = 1;

# Watch for changes in CSV files
$extra_watch_files = "data/*.csv";

# Force rebuild if CSV files change
$force_mode = 1;

# Custom build sequence: conditionally sort CSV files, then compile
$pdflatex = "if [ data/*.csv -nt data/.last_sorted ] 2>/dev/null || [ ! -f data/.last_sorted ]; then python3 sort_csvs.py && touch data/.last_sorted; fi && pdflatex %O %S";
