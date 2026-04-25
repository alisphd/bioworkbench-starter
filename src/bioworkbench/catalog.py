from __future__ import annotations

from bioworkbench.core.models import ToolSpec
from bioworkbench.core.registry import ToolRegistry


def build_registry() -> ToolRegistry:
    tools = [
        ToolSpec(
            id="fasta_formatter",
            name="FASTA Formatter",
            category="Utilities",
            description="Clean FASTA input, validate sequence characters, normalize case, and wrap lines to a chosen width.",
            status="ready",
            next_steps=(
                "Add file import and export.",
                "Support nucleotide and protein-specific validation profiles.",
            ),
        ),
        ToolSpec(
            id="sequence_summary",
            name="Sequence Summary",
            category="Utilities",
            description="Inspect FASTA datasets with per-record length, sequence type, GC content, and ambiguity counts.",
            status="ready",
            next_steps=(
                "Add CSV export for per-record metrics.",
                "Extend summaries with amino-acid composition and k-mer counts.",
            ),
        ),
        ToolSpec(
            id="sequence_transform",
            name="Sequence Transform",
            category="Utilities",
            description="Apply reverse, reverse-complement, transcription, and translation transforms to FASTA records.",
            status="ready",
            next_steps=(
                "Add frame-aware translation previews and ORF detection.",
                "Support separate DNA and protein validation warnings.",
            ),
        ),
        ToolSpec(
            id="kmer_counter",
            name="K-mer Counter",
            category="Utilities",
            description="Count the most frequent k-mers across FASTA records for quick composition screening.",
            status="ready",
            next_steps=(
                "Add CSV export and per-record grouping.",
                "Add visual distribution charts for large datasets.",
            ),
        ),
        ToolSpec(
            id="blast_explorer",
            name="BLAST Explorer",
            category="Mining Suite",
            description="Run local BLAST workflows with saved presets for nucleotide and protein search modes.",
            external_tools=("BLAST+",),
            next_steps=(
                "Build a database selector and command composer.",
                "Parse tabular output into filterable result tables.",
            ),
        ),
        ToolSpec(
            id="motif_finder",
            name="Motif Finder",
            category="Mining Suite",
            description="Search exact motifs across FASTA records and report all overlapping hit positions.",
            status="ready",
            next_steps=(
                "Add degenerate motif support and regex mode.",
                "Export match tables to CSV or Excel.",
            ),
        ),
        ToolSpec(
            id="orf_finder",
            name="ORF Finder",
            category="Mining Suite",
            description="Find open reading frames in nucleotide FASTA records across forward and reverse frames.",
            status="ready",
            next_steps=(
                "Add ORF FASTA export and genomic coordinate mapping.",
                "Support custom start and stop codon tables.",
            ),
        ),
        ToolSpec(
            id="hmm_build",
            name="HMM Build",
            category="Mining Suite",
            description="Create HMM profiles from curated alignments using local HMMER binaries.",
            external_tools=("HMMER",),
            next_steps=(
                "Add alignment import and profile output handling.",
                "Validate model names and output destinations.",
            ),
        ),
        ToolSpec(
            id="hmm_search",
            name="HMM Search",
            category="Mining Suite",
            description="Search protein sets with HMM profiles and return domain-based hits.",
            external_tools=("HMMER",),
            next_steps=(
                "Collect profile, query, and threshold settings.",
                "Summarize hits with sortable tables and exports.",
            ),
        ),
        ToolSpec(
            id="alignment_studio",
            name="Alignment Studio",
            category="Classification Suite",
            description="Manage sequence alignment and trimming workflows for downstream analysis.",
            external_tools=("MUSCLE", "ClustalW", "trimAl"),
            next_steps=(
                "Expose aligner selection and parameter presets.",
                "Preview alignment statistics before exporting.",
            ),
        ),
        ToolSpec(
            id="phylogenetic_analysis",
            name="Phylogenetic Analysis",
            category="Classification Suite",
            description="Prepare trees from alignments and evolve toward a full IQ-TREE workflow.",
            external_tools=("IQ-TREE",),
            next_steps=(
                "Add model selection and bootstrap controls.",
                "Render tree summaries after execution.",
            ),
        ),
        ToolSpec(
            id="kaks_analyzer",
            name="Ka/Ks Analyzer",
            category="Evolutionary Analysis",
            description="Compare coding sequences and ortholog pairs to estimate selective pressure.",
            external_tools=("KaKs_Calculator", "PAL2NAL"),
            next_steps=(
                "Validate ortholog pair files before submission.",
                "Surface pairwise results and significance flags.",
            ),
        ),
        ToolSpec(
            id="homolog_finder",
            name="Homolog Finder",
            category="Evolutionary Analysis",
            description="Find candidate homologs and orthologs from local protein collections.",
            external_tools=("DIAMOND",),
            next_steps=(
                "Build a database workflow and query launcher.",
                "Rank hits with identity and coverage filters.",
            ),
        ),
        ToolSpec(
            id="gene_density_map",
            name="Gene Density Map",
            category="Visualization",
            description="Summarize feature density along chromosomes or scaffolds from annotation data.",
            next_steps=(
                "Accept GFF3, FASTA index, and optional gene family filters.",
                "Render ideogram-style summaries with export support.",
            ),
        ),
        ToolSpec(
            id="gc_window_scanner",
            name="GC Window Scanner",
            category="Visualization",
            description="Scan GC content across sliding windows to reveal local compositional shifts.",
            status="ready",
            next_steps=(
                "Add line charts and threshold highlighting.",
                "Support downloadable window tables.",
            ),
        ),
        ToolSpec(
            id="expression_heatmap",
            name="Expression Heatmap",
            category="Visualization",
            description="Create expression heatmaps from matrix-like experiment tables.",
            next_steps=(
                "Add spreadsheet import and metadata mapping.",
                "Support clustering and palette presets.",
            ),
        ),
        ToolSpec(
            id="primer_designer",
            name="Primer Designer",
            category="Primer Design",
            description="Generate simple forward and reverse primer candidates from nucleotide sequences with GC and Tm filters.",
            status="ready",
            next_steps=(
                "Upgrade candidate scoring into paired primer selection.",
                "Add optional Primer3 integration for advanced design rules.",
            ),
        ),
    ]
    return ToolRegistry(tools)
