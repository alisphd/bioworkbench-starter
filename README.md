# BioWorkbench Starter

`BioWorkbench Starter` is a modular bioinformatics workbench that now supports both:

- a desktop application for richer local workflows
- a browser-based demo so people can test core tools online

The project intentionally gives you:

- a modular `PySide6` desktop shell
- a dashboard with quick-launch cards for ready tools
- a registry for organizing tools by suite
- a reusable command runner for future BLAST/HMMER/Primer3 integrations
- several working sequence-analysis tools today
- a `Streamlit` demo app for public testing
- GitHub CI and deployment guidance for the next step

## What is already included

- `Utilities`
  - `FASTA Formatter`
  - `Sequence Summary`
  - `Sequence Transform`
- `Mining Suite`
  - `Motif Finder`
  - `BLAST Explorer` placeholder
  - `HMM Build` placeholder
  - `HMM Search` placeholder
- `Classification Suite`
  - `Alignment Studio` placeholder
  - `Phylogenetic Analysis` placeholder
- `Evolutionary Analysis`
  - `Ka/Ks Analyzer` placeholder
  - `Homolog Finder` placeholder
- `Visualization`
  - `Gene Density Map` placeholder
  - `Expression Heatmap` placeholder
- `Primer Design`
  - `Primer Designer` with a simple heuristic candidate finder

## Project structure

```text
bio-workbench-starter/
├── .github/workflows/
├── .streamlit/
├── data/
├── docs/
├── src/
│   └── bioworkbench/
│       ├── app.py
│       ├── catalog.py
│       ├── main.py
│       ├── web_demo.py
│       ├── core/
│       ├── tools/
│       └── ui/
├── streamlit_app.py
└── tests/
```

## Desktop quick start

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

## Web demo quick start

```bash
cd D:\Codex\bio-workbench-starter
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-demo.txt
streamlit run streamlit_app.py
```

## Ready workflows

- Format FASTA records with validation and line wrapping.
- Summarize sequence type, length, GC content, and ambiguous bases.
- Reverse, reverse-complement, transcribe, and translate sequences.
- Search exact motifs across all FASTA records.
- Suggest simple forward and reverse primer candidates from nucleotide sequences.

## Why this layout is better for a larger project

- Tool metadata lives in one registry instead of being hard-coded across the UI.
- The desktop app and web demo reuse the same pure-Python sequence logic.
- External tool execution is isolated in a reusable runner.
- Each feature can become its own module without turning the main window into a giant script.
- You can grow from a simple utility app into a full suite without rewriting the foundation.

## Suggested next steps

1. Choose the next external-tool workflow, such as local BLAST or HMMER.
2. Wrap the binary with `CommandRunner`.
3. Replace the corresponding placeholder page with a real widget.
4. Extend the Streamlit demo only for workflows that can safely run in a hosted environment.
5. Push the repo to GitHub and follow [docs/publish-and-deploy.md](docs/publish-and-deploy.md).

More implementation guidance is in [docs/project-blueprint.md](docs/project-blueprint.md).

