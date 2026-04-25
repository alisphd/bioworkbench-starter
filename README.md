# BioWorkbench Starter

[![Live Demo](https://img.shields.io/badge/LIVE%20DEMO-bioworkbench--starter.streamlit.app-0f766e?style=for-the-badge&logo=streamlit&logoColor=white)](https://bioworkbench-starter.streamlit.app/)
[![Project Page](https://img.shields.io/badge/GITHUB%20PAGES-alisphd.github.io%2Fbioworkbench--starter-2563eb?style=for-the-badge&logo=githubpages&logoColor=white)](https://alisphd.github.io/bioworkbench-starter/)
[![GitHub Repo](https://img.shields.io/badge/GITHUB-alisphd%2Fbioworkbench--starter-111827?style=for-the-badge&logo=github&logoColor=white)](https://github.com/alisphd/bioworkbench-starter)
[![Python](https://img.shields.io/badge/PYTHON-3.11+-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/STREAMLIT-live%20web%20app-ff4b4b?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![PySide6](https://img.shields.io/badge/DESKTOP-PySide6-16a34a?style=for-the-badge)](https://doc.qt.io/qtforpython-6/)

`BioWorkbench Starter` is a modular bioinformatics workbench with a desktop application for local workflows and a browser-based demo for quick public testing.

Live demo: [bioworkbench-starter.streamlit.app](https://bioworkbench-starter.streamlit.app/)
Project page: [alisphd.github.io/bioworkbench-starter](https://alisphd.github.io/bioworkbench-starter/)

## What It Does

- Formats, validates, and wraps FASTA records.
- Summarizes sequence type, length, GC content, and ambiguity counts.
- Transforms sequences with reverse, reverse-complement, DNA/RNA conversion, and translation modes.
- Searches exact motifs across FASTA records.
- Finds ORFs in nucleotide sequences.
- Scans GC content across sliding windows.
- Counts top k-mers.
- Suggests simple primer candidates with GC and Tm filters.

## Included Tool Areas

- `Utilities`: FASTA Formatter, Sequence Summary, Sequence Transform, K-mer Counter
- `Mining Suite`: Motif Finder, ORF Finder, BLAST Explorer placeholder, HMMER placeholders
- `Visualization`: GC Window Scanner, Gene Density Map placeholder, Expression Heatmap placeholder
- `Primer Design`: Primer Designer
- `Classification`: Alignment Studio and Phylogenetic Analysis placeholders
- `Evolutionary Analysis`: Ka/Ks Analyzer and Homolog Finder placeholders

## Project Structure

```text
bio-workbench-starter/
|-- .github/workflows/
|-- .streamlit/
|-- data/
|-- docs/
|-- src/
|   `-- bioworkbench/
|       |-- app.py
|       |-- catalog.py
|       |-- main.py
|       |-- web_demo.py
|       |-- core/
|       |-- tools/
|       `-- ui/
|-- streamlit_app.py
`-- tests/
```

## Desktop Quick Start

```bash
cd D:\Codex\bio-workbench-starter
python -m venv .venv
.venv\Scripts\activate
pip install -e .[desktop,dev]
bioworkbench
```

You can also run:

```bash
python -m bioworkbench.main
```

## Web Demo Quick Start

```bash
cd D:\Codex\bio-workbench-starter
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Why This Layout Works

- Tool metadata lives in one registry instead of being hard-coded across the UI.
- The desktop app and web demo reuse the same pure-Python sequence logic.
- External tool execution is isolated in a reusable runner.
- Each feature can become its own module without turning the main window into a giant script.
- Hosted tools stay lightweight, while local desktop workflows can later call BLAST, HMMER, IQ-TREE, DIAMOND, and Primer3.

## Roadmap

1. Add real local BLAST database building and search workflows.
2. Add HMMER profile build and search pages.
3. Add alignment and phylogenetic analysis modules.
4. Add exportable reports for each workflow.
5. Improve the desktop UI to match the newer web dashboard direction.

More implementation guidance is in [docs/project-blueprint.md](docs/project-blueprint.md).
