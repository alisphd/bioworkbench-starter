# Project Blueprint

## Product direction

Build an offline-first desktop workbench that helps a researcher move from raw sequence files to interpretable outputs without juggling many disconnected tools.

## Architecture

### 1. Tool catalog

Every tool is registered in one place with:

- `id`
- `name`
- `category`
- `description`
- `status`
- `external_tools`
- `next_steps`

That keeps the navigation, landing page, and future permissions model aligned.

### 2. UI shell

The main window should stay lightweight. It only needs to:

- render the sidebar
- switch between pages
- create tool pages on demand

Actual tool logic belongs in dedicated modules under `tools/` or `ui/`.

### 3. Tool execution

Use `CommandRunner` when a feature needs to call external executables such as:

- `blastn`, `blastp`, `blastx`
- `hmmbuild`, `hmmsearch`
- `muscle`, `clustalw`, `iqtree`
- `primer3_core`

That runner gives you one place to add:

- logging
- timeout handling
- environment setup
- job history
- future async execution

## Recommended roadmap

### Phase 1

- FASTA import, validation, and formatting
- sequence statistics
- local file management

### Phase 2

- BLAST wrapper with preset tasks
- HMM build/search pages
- alignment and trimming workflows

### Phase 3

- phylogenetic tree building
- Ka/Ks analysis pipelines
- genomic visualization

### Phase 4

- project sessions
- exportable reports
- batch jobs
- reproducibility metadata

## How to add a real tool

1. Create a new module under `src/bioworkbench/tools/`.
2. Add parsing, validation, and pure functions first.
3. Build a dedicated widget or page for the interaction model.
4. Register it in `catalog.py`.
5. Replace the placeholder page mapping in `ui/main_window.py`.
6. Add at least one unit test for its core logic.

## Good early features

If you want quick wins, build these next:

- sequence summary and GC content
- local BLAST database builder
- HMM search page
- primer design launcher
- expression heatmap importer

