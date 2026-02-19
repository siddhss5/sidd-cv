.PHONY: help sync-data sync-pubs build clean test all

help:
	@echo "CV Build Tasks:"
	@echo "  make sync-data   - Fetch latest YAML from website repo and regenerate CSVs"
	@echo "  make sync-pubs   - Fetch latest publications from personalrobotics/pubs"
	@echo "  make build       - Compile CV PDF"
	@echo "  make clean       - Remove auxiliary files"
	@echo "  make test        - Validate YAML data"
	@echo "  make all         - Sync data + pubs + build"

sync-data:
	@echo "📥 Fetching latest YAML and generating CSVs..."
	@python3 yaml2csv.py --owner siddhss5 --repo siddhss5.github.io --branch main --output-dir data/
	@echo "✅ CSV files updated"

sync-pubs:
	@./sync-pubs.sh

build:
	@echo "🔨 Building CV..."
	@latexmk -pdf -silent sidd-cv.tex
	@echo "✅ CV built successfully"

clean:
	@echo "🧹 Cleaning auxiliary files..."
	@latexmk -c
	@rm -f *.bbl *.blg
	@echo "✅ Clean complete"

test:
	@echo "🔍 Validating YAML data..."
	@python3 yaml2csv.py --owner siddhss5 --repo siddhss5.github.io --branch main --output-dir data/ --validate

all: sync-data sync-pubs build
	@echo "✅ All tasks complete!"
