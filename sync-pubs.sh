#!/bin/bash
# Sync publications from personalrobotics/pubs and rebuild CV

set -e  # Exit on error

echo "📚 Syncing publications from personalrobotics/pubs..."
echo

# Fetch latest BibTeX files
cd pubs
for file in siddpubs-journal.bib siddpubs-conf.bib siddpubs-misc.bib; do
  echo "📥 Fetching ${file}..."
  curl -sf "https://raw.githubusercontent.com/personalrobotics/pubs/master/${file}" -o "${file}"
  echo "✅ Updated ${file}"
done
cd ..

echo
echo "📊 Changes:"
git diff --stat pubs/*.bib || echo "No changes"

echo
echo "🔨 Rebuilding CV..."
latexmk -pdf -silent sidd-cv.tex

echo
echo "✅ Done! CV updated with latest publications."
echo
echo "To commit changes:"
echo "  git add pubs/*.bib sidd-cv.pdf"
echo "  git commit -m 'Update publications from upstream'"
echo "  git push"
