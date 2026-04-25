from __future__ import annotations

import streamlit as st

from bioworkbench.catalog import build_registry
from bioworkbench.tools.fasta_formatter import EXAMPLE_FASTA, format_fasta
from bioworkbench.tools.sequence_ops import (
    count_kmers,
    design_primers,
    find_motif_matches,
    find_orfs,
    format_records,
    gc_windows,
    parse_fasta,
    summarize_records,
    transform_records,
)


TOOL_PAGES = [
    "Dashboard",
    "FASTA Formatter",
    "Sequence Summary",
    "Sequence Transform",
    "Motif Finder",
    "ORF Finder",
    "GC Window Scanner",
    "K-mer Counter",
    "Primer Designer",
]


def render() -> None:
    st.set_page_config(
        page_title="BioWorkbench",
        page_icon=":dna:",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _inject_theme()

    registry = build_registry()
    ready_tools = registry.ready_tools()

    with st.sidebar:
        st.markdown('<div class="sidebar-title">BioWorkbench</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-subtitle">Sequence tools for plant genomics workflows</div>', unsafe_allow_html=True)
        page = st.radio("Workspace", TOOL_PAGES, label_visibility="collapsed")
        st.markdown('<div class="sidebar-rule"></div>', unsafe_allow_html=True)
        st.link_button("Live project site", "https://alisphd.github.io/bioworkbench-starter/", use_container_width=True)
        st.link_button("GitHub repository", "https://github.com/alisphd/bioworkbench-starter", use_container_width=True)

    if page == "Dashboard":
        _render_dashboard(registry, ready_tools)
    elif page == "FASTA Formatter":
        _render_fasta_formatter()
    elif page == "Sequence Summary":
        _render_sequence_summary()
    elif page == "Sequence Transform":
        _render_sequence_transform()
    elif page == "Motif Finder":
        _render_motif_finder()
    elif page == "ORF Finder":
        _render_orf_finder()
    elif page == "GC Window Scanner":
        _render_gc_window_scanner()
    elif page == "K-mer Counter":
        _render_kmer_counter()
    elif page == "Primer Designer":
        _render_primer_designer()


def _render_dashboard(registry, ready_tools) -> None:
    _page_header(
        "BioWorkbench",
        "Live browser workbench for FASTA inspection, motif search, ORF discovery, GC scanning, k-mer counts, and primer suggestions.",
    )

    metric_cols = st.columns(4)
    metric_cols[0].metric("Suites", len(registry.categories()))
    metric_cols[1].metric("Ready tools", len(ready_tools))
    metric_cols[2].metric("Hosted app", "Streamlit")
    metric_cols[3].metric("Core", "Python")

    st.markdown('<div class="section-title">Ready tools</div>', unsafe_allow_html=True)
    rows = [ready_tools[index : index + 3] for index in range(0, len(ready_tools), 3)]
    for row in rows:
        columns = st.columns(3)
        for column, tool in zip(columns, row):
            with column:
                st.markdown(
                    f"""
                    <div class="tool-card">
                      <div class="tool-card-label">{tool.category}</div>
                      <div class="tool-card-title">{tool.name}</div>
                      <div class="tool-card-body">{tool.description}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown('<div class="section-title">Planned local integrations</div>', unsafe_allow_html=True)
    for category in registry.categories():
        planned = [tool for tool in registry.by_category(category) if not tool.is_ready]
        if not planned:
            continue
        with st.expander(category):
            for tool in planned:
                external = f" Uses {', '.join(tool.external_tools)}." if tool.external_tools else ""
                st.write(f"{tool.name}: {tool.description}{external}")


def _render_fasta_formatter() -> None:
    _page_header("FASTA Formatter", "Clean FASTA input, normalize case, validate characters, and wrap lines.")
    left, right = st.columns([2, 1])
    with right:
        line_width = st.number_input("Wrap width", min_value=10, max_value=200, value=60)
        uppercase = st.toggle("Uppercase sequence", value=True)
    with left:
        fasta_text = _fasta_editor("formatter-input")

    if st.button("Format FASTA", type="primary", use_container_width=True):
        try:
            result = format_fasta(fasta_text, line_width=int(line_width), uppercase=uppercase)
            st.success(f"Formatted {result.record_count} record(s) across {result.residue_count} residues.")
            st.code(result.formatted_text, language="text")
            st.download_button("Download formatted FASTA", result.formatted_text, "formatted_sequences.fasta")
        except ValueError as exc:
            st.error(str(exc))


def _render_sequence_summary() -> None:
    _page_header("Sequence Summary", "Inspect sequence type, length, GC content, ambiguity, and preview values.")
    fasta_text = _fasta_editor("summary-input")
    if st.button("Summarize sequences", type="primary", use_container_width=True):
        try:
            summaries = summarize_records(parse_fasta(fasta_text, uppercase=True))
            st.success(f"Summarized {len(summaries)} record(s).")
            st.dataframe(
                [
                    {
                        "Header": item.header,
                        "Type": item.sequence_type,
                        "Length": item.length,
                        "GC %": None if item.gc_percent is None else round(item.gc_percent, 2),
                        "Ambiguous Ns": item.ambiguous_count,
                        "Preview": item.preview,
                    }
                    for item in summaries
                ],
                use_container_width=True,
                hide_index=True,
            )
        except ValueError as exc:
            st.error(str(exc))


def _render_sequence_transform() -> None:
    _page_header("Sequence Transform", "Reverse, complement, transcribe, translate, and export transformed records.")
    options = {
        "Uppercase": "uppercase",
        "Reverse": "reverse",
        "Reverse complement": "reverse_complement",
        "DNA to RNA": "dna_to_rna",
        "RNA to DNA": "rna_to_dna",
        "Translate": "translate",
    }
    left, right = st.columns([2, 1])
    with left:
        fasta_text = _fasta_editor("transform-input")
    with right:
        mode_label = st.selectbox("Transform", list(options.keys()))
        frame = st.number_input("Frame", min_value=1, max_value=3, value=1, disabled=mode_label != "Translate")
        line_width = st.number_input("Wrap width", min_value=10, max_value=200, value=60)

    if st.button("Apply transform", type="primary", use_container_width=True):
        try:
            records = parse_fasta(fasta_text, uppercase=True)
            transformed = transform_records(records, options[mode_label], frame=int(frame))
            output = format_records(transformed, line_width=int(line_width))
            st.success(f"Transformed {len(transformed)} record(s).")
            st.code(output, language="text")
            st.download_button("Download transformed FASTA", output, "transformed_sequences.fasta")
        except ValueError as exc:
            st.error(str(exc))


def _render_motif_finder() -> None:
    _page_header("Motif Finder", "Search exact motifs and report overlapping hit positions.")
    fasta_text = _fasta_editor("motif-input")
    col1, col2 = st.columns([2, 1])
    with col1:
        motif = st.text_input("Motif", value="ATG")
    with col2:
        case_sensitive = st.toggle("Case sensitive", value=False)

    if st.button("Find motif", type="primary", use_container_width=True):
        try:
            matches = find_motif_matches(parse_fasta(fasta_text, uppercase=True), motif, case_sensitive=case_sensitive)
            if not matches:
                st.info("No matches found.")
                return
            st.success(f"Found {len(matches)} match(es).")
            st.dataframe(
                [
                    {
                        "Header": match.header,
                        "Start": match.start,
                        "End": match.end,
                        "Match": match.matched_text,
                    }
                    for match in matches
                ],
                use_container_width=True,
                hide_index=True,
            )
        except ValueError as exc:
            st.error(str(exc))


def _render_orf_finder() -> None:
    _page_header("ORF Finder", "Find open reading frames from nucleotide FASTA records.")
    left, right = st.columns([2, 1])
    with left:
        fasta_text = _fasta_editor("orf-input")
    with right:
        min_length = st.number_input("Minimum ORF length", min_value=3, max_value=10000, value=30, step=3)
        include_reverse = st.toggle("Include reverse strand", value=True)

    if st.button("Find ORFs", type="primary", use_container_width=True):
        try:
            hits = find_orfs(parse_fasta(fasta_text, uppercase=True), min_length=int(min_length), include_reverse=include_reverse)
            if not hits:
                st.info("No ORFs passed the current filters.")
                return
            st.success(f"Found {len(hits)} ORF(s).")
            st.dataframe(
                [
                    {
                        "Header": hit.header,
                        "Frame": hit.frame,
                        "Start": hit.start,
                        "End": hit.end,
                        "Length": hit.length,
                        "Protein": hit.protein_sequence,
                    }
                    for hit in hits
                ],
                use_container_width=True,
                hide_index=True,
            )
        except ValueError as exc:
            st.error(str(exc))


def _render_gc_window_scanner() -> None:
    _page_header("GC Window Scanner", "Scan GC percentage across sliding windows.")
    left, right = st.columns([2, 1])
    with left:
        fasta_text = _fasta_editor("gc-window-input")
    with right:
        window_size = st.number_input("Window size", min_value=5, max_value=10000, value=12)
        step_size = st.number_input("Step size", min_value=1, max_value=10000, value=6)

    if st.button("Scan GC windows", type="primary", use_container_width=True):
        try:
            windows = gc_windows(parse_fasta(fasta_text, uppercase=True), window_size=int(window_size), step_size=int(step_size))
            if not windows:
                st.info("No nucleotide records were available for GC scanning.")
                return
            rows = [
                {
                    "Header": window.header,
                    "Start": window.start,
                    "End": window.end,
                    "GC %": None if window.gc_percent is None else round(window.gc_percent, 2),
                }
                for window in windows
            ]
            st.success(f"Scanned {len(windows)} window(s).")
            st.dataframe(rows, use_container_width=True, hide_index=True)
            st.vega_lite_chart(
                rows,
                {
                    "mark": {"type": "line", "point": True},
                    "encoding": {
                        "x": {"field": "Start", "type": "quantitative"},
                        "y": {"field": "GC %", "type": "quantitative"},
                        "color": {"field": "Header", "type": "nominal"},
                        "tooltip": [
                            {"field": "Header", "type": "nominal"},
                            {"field": "Start", "type": "quantitative"},
                            {"field": "End", "type": "quantitative"},
                            {"field": "GC %", "type": "quantitative"},
                        ],
                    },
                },
                use_container_width=True,
            )
        except ValueError as exc:
            st.error(str(exc))


def _render_kmer_counter() -> None:
    _page_header("K-mer Counter", "Rank the most frequent k-mers in FASTA records.")
    left, right = st.columns([2, 1])
    with left:
        fasta_text = _fasta_editor("kmer-input")
    with right:
        k = st.number_input("K-mer size", min_value=1, max_value=12, value=3)
        top_n = st.number_input("Top N", min_value=1, max_value=100, value=20)
        nucleotide_only = st.toggle("Nucleotide-only mode", value=True)

    if st.button("Count k-mers", type="primary", use_container_width=True):
        try:
            counts = count_kmers(parse_fasta(fasta_text, uppercase=True), k=int(k), top_n=int(top_n), nucleotide_only=nucleotide_only)
            if not counts:
                st.info("No k-mers were counted with the current settings.")
                return
            rows = [
                {
                    "K-mer": item.kmer,
                    "Count": item.count,
                    "Frequency %": round(item.frequency_percent, 2),
                }
                for item in counts
            ]
            st.success(f"Found {len(rows)} ranked k-mer(s).")
            st.dataframe(rows, use_container_width=True, hide_index=True)
            st.vega_lite_chart(
                rows,
                {
                    "mark": "bar",
                    "encoding": {
                        "x": {"field": "K-mer", "type": "nominal", "sort": "-y"},
                        "y": {"field": "Count", "type": "quantitative"},
                        "tooltip": [
                            {"field": "K-mer", "type": "nominal"},
                            {"field": "Count", "type": "quantitative"},
                            {"field": "Frequency %", "type": "quantitative"},
                        ],
                    },
                },
                use_container_width=True,
            )
        except ValueError as exc:
            st.error(str(exc))


def _render_primer_designer() -> None:
    _page_header("Primer Designer", "Suggest simple primer candidates with GC and Wallace Tm filters.")
    left, right = st.columns([2, 1])
    with left:
        fasta_text = _fasta_editor("primer-input")
    with right:
        primer_length = st.number_input("Primer length", min_value=16, max_value=30, value=20)
        min_gc = st.number_input("Min GC", min_value=0.0, max_value=100.0, value=40.0)
        max_gc = st.number_input("Max GC", min_value=0.0, max_value=100.0, value=60.0)
        top_n = st.number_input("Top N", min_value=1, max_value=20, value=5)

    if st.button("Suggest primers", type="primary", use_container_width=True):
        try:
            result = design_primers(
                parse_fasta(fasta_text, uppercase=True),
                primer_length=int(primer_length),
                min_gc=float(min_gc),
                max_gc=float(max_gc),
                top_n=int(top_n),
            )
            if result.scanned_records == 0:
                st.info("No DNA or RNA records were found to scan.")
                return
            rows = []
            for candidate in (*result.forward, *result.reverse):
                rows.append(
                    {
                        "Direction": candidate.direction,
                        "Header": candidate.header,
                        "Start": candidate.start,
                        "End": candidate.end,
                        "Sequence": candidate.sequence,
                        "GC %": round(candidate.gc_percent, 2),
                        "Tm C": round(candidate.tm_celsius, 1),
                        "Score": round(candidate.score, 2),
                    }
                )
            st.success(f"Returned {len(rows)} primer candidate(s) from {result.scanned_records} scanned record(s).")
            st.dataframe(rows, use_container_width=True, hide_index=True)
        except ValueError as exc:
            st.error(str(exc))


def _page_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="page-header">
          <div class="eyebrow">BioWorkbench Starter</div>
          <h1>{title}</h1>
          <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _fasta_editor(key: str) -> str:
    return st.text_area(
        "FASTA input",
        value=EXAMPLE_FASTA,
        height=260,
        key=key,
        label_visibility="collapsed",
    )


def _inject_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg: #f6f7f4;
            --panel: #ffffff;
            --ink: #17201a;
            --muted: #5c6670;
            --line: #dce3dc;
            --green: #0f766e;
            --blue: #2563eb;
            --amber: #b45309;
        }
        .stApp {
            background:
                linear-gradient(180deg, rgba(246,247,244,0.96), rgba(239,243,239,1)),
                radial-gradient(circle at 90% 4%, rgba(37,99,235,0.12), transparent 28%);
            color: var(--ink);
        }
        section[data-testid="stSidebar"] {
            background: #101820;
            border-right: 1px solid rgba(255,255,255,0.08);
        }
        section[data-testid="stSidebar"] * {
            color: #f7fbff;
        }
        .sidebar-title {
            font-size: 1.35rem;
            font-weight: 800;
            letter-spacing: 0;
            margin: 0.25rem 0 0.15rem;
        }
        .sidebar-subtitle {
            color: #b8c4cc;
            font-size: 0.9rem;
            line-height: 1.45;
            margin-bottom: 1rem;
        }
        .sidebar-rule {
            border-top: 1px solid rgba(255,255,255,0.14);
            margin: 1rem 0;
        }
        .main .block-container {
            max-width: 1220px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }
        .page-header {
            border-bottom: 1px solid var(--line);
            padding-bottom: 1.1rem;
            margin-bottom: 1.2rem;
        }
        .page-header h1 {
            color: var(--ink);
            font-size: 2.35rem;
            line-height: 1.1;
            margin: 0.15rem 0 0.45rem;
            letter-spacing: 0;
        }
        .page-header p {
            max-width: 760px;
            color: var(--muted);
            font-size: 1rem;
            line-height: 1.55;
            margin: 0;
        }
        .eyebrow {
            color: var(--green);
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .section-title {
            font-size: 1.05rem;
            font-weight: 800;
            margin: 1.4rem 0 0.7rem;
            color: var(--ink);
        }
        div[data-testid="stMetric"] {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 0.9rem 1rem;
            box-shadow: 0 10px 24px rgba(16,24,32,0.05);
        }
        .tool-card {
            min-height: 176px;
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 10px 24px rgba(16,24,32,0.05);
        }
        .tool-card-label {
            color: var(--green);
            font-size: 0.72rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.5rem;
        }
        .tool-card-title {
            color: var(--ink);
            font-size: 1.08rem;
            font-weight: 800;
            margin-bottom: 0.45rem;
        }
        .tool-card-body {
            color: var(--muted);
            line-height: 1.45;
            font-size: 0.92rem;
        }
        .stButton > button,
        .stDownloadButton > button,
        .stLinkButton > a {
            border-radius: 7px;
            font-weight: 750;
            border: 1px solid rgba(15,118,110,0.22);
        }
        .stTextArea textarea {
            border-radius: 8px;
            border-color: var(--line);
            font-family: "Cascadia Code", Consolas, monospace;
            line-height: 1.45;
        }
        div[data-testid="stDataFrame"] {
            border: 1px solid var(--line);
            border-radius: 8px;
            overflow: hidden;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
