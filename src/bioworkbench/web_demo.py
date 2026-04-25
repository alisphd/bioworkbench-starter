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

TOOL_PAGE_BY_ID = {
    "fasta_formatter": "FASTA Formatter",
    "sequence_summary": "Sequence Summary",
    "sequence_transform": "Sequence Transform",
    "motif_finder": "Motif Finder",
    "orf_finder": "ORF Finder",
    "gc_window_scanner": "GC Window Scanner",
    "kmer_counter": "K-mer Counter",
    "primer_designer": "Primer Designer",
}

TOOL_META = {
    "fasta_formatter": {
        "icon": "fasta",
        "accent": "#0f766e",
        "preview": '<div class="seq-preview"><span>A</span><span>T</span><span>G</span><span>C</span><span>G</span><span>T</span></div>',
        "tag": "Clean FASTA",
    },
    "sequence_summary": {
        "icon": "summary",
        "accent": "#2563eb",
        "preview": '<div class="mini-bars"><i style="height:38%"></i><i style="height:78%"></i><i style="height:54%"></i><i style="height:90%"></i></div>',
        "tag": "Length and GC",
    },
    "sequence_transform": {
        "icon": "transform",
        "accent": "#7c3aed",
        "preview": '<div class="flow-preview"><span>DNA</span><b></b><span>RNA</span><b></b><span>AA</span></div>',
        "tag": "Convert records",
    },
    "motif_finder": {
        "icon": "motif",
        "accent": "#dc2626",
        "preview": '<div class="hit-preview"><span></span><strong>ATG</strong><span></span><strong>ATG</strong></div>',
        "tag": "Find motifs",
    },
    "orf_finder": {
        "icon": "orf",
        "accent": "#b45309",
        "preview": '<div class="orf-preview"><span></span><span class="orf-long"></span><span></span></div>',
        "tag": "Reading frames",
    },
    "gc_window_scanner": {
        "icon": "gc",
        "accent": "#0891b2",
        "preview": '<div class="wave-preview"><i></i><i></i><i></i><i></i><i></i></div>',
        "tag": "GC windows",
    },
    "kmer_counter": {
        "icon": "kmer",
        "accent": "#4f46e5",
        "preview": '<div class="kmer-preview"><span>ATG</span><span>GCA</span><span>TTA</span></div>',
        "tag": "Rank k-mers",
    },
    "primer_designer": {
        "icon": "primer",
        "accent": "#16a34a",
        "preview": '<div class="primer-preview"><span>FWD</span><b></b><span>REV</span></div>',
        "tag": "Primer picks",
    },
}


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

    if "current_page" not in st.session_state:
        st.session_state.current_page = "Dashboard"

    with st.sidebar:
        st.markdown(_sidebar_brand(), unsafe_allow_html=True)
        active_index = TOOL_PAGES.index(st.session_state.current_page)
        selected_page = st.radio("Workspace", TOOL_PAGES, index=active_index, label_visibility="collapsed")
        st.session_state.current_page = selected_page
        st.markdown('<div class="sidebar-rule"></div>', unsafe_allow_html=True)
        st.link_button("Project site", "https://alisphd.github.io/bioworkbench-starter/", use_container_width=True)
        st.link_button("GitHub repo", "https://github.com/alisphd/bioworkbench-starter", use_container_width=True)

    page = st.session_state.current_page
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
    st.markdown(_dashboard_hero(len(ready_tools), len(registry.categories())), unsafe_allow_html=True)
    st.markdown(_badge_bar(), unsafe_allow_html=True)

    st.markdown('<div class="section-title">Ready tool bench</div>', unsafe_allow_html=True)
    rows = [ready_tools[index : index + 4] for index in range(0, len(ready_tools), 4)]
    for row in rows:
        columns = st.columns(4)
        for column, tool in zip(columns, row):
            with column:
                _render_tool_card(tool)

    st.markdown('<div class="section-title">Local workflow roadmap</div>', unsafe_allow_html=True)
    planned = [tool for tool in registry.all() if not tool.is_ready]
    roadmap_rows = [planned[index : index + 3] for index in range(0, len(planned), 3)]
    for row in roadmap_rows:
        columns = st.columns(3)
        for column, tool in zip(columns, row):
            with column:
                external = ", ".join(tool.external_tools) if tool.external_tools else "Python workflow"
                st.markdown(
                    f"""
                    <div class="roadmap-card">
                      <div class="roadmap-tag">{tool.category}</div>
                      <div class="roadmap-title">{tool.name}</div>
                      <div class="roadmap-meta">{external}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def _render_tool_card(tool) -> None:
    meta = TOOL_META.get(
        tool.id,
        {"icon": "fasta", "accent": "#0f766e", "preview": "", "tag": tool.category},
    )
    st.markdown(
        f"""
        <div class="tool-card" style="--accent: {meta["accent"]};">
          <div class="tool-card-top">
            <div class="tool-icon">{_icon_svg(meta["icon"])}</div>
            <div class="tool-tag">{meta["tag"]}</div>
          </div>
          <div class="tool-title">{tool.name}</div>
          <div class="tool-body">{tool.description}</div>
          <div class="tool-preview">{meta["preview"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    page_name = TOOL_PAGE_BY_ID.get(tool.id)
    if page_name and st.button(f"Open {tool.name}", key=f"open-{tool.id}", use_container_width=True):
        st.session_state.current_page = page_name
        st.rerun()


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
    icon_key = next((meta["icon"] for tool_id, meta in TOOL_META.items() if TOOL_PAGE_BY_ID.get(tool_id) == title), "fasta")
    st.markdown(
        f"""
        <div class="page-header">
          <div class="page-icon">{_icon_svg(icon_key)}</div>
          <div>
            <div class="eyebrow">BioWorkbench Starter</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
          </div>
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


def _sidebar_brand() -> str:
    return f"""
    <div class="sidebar-brand">
      <div class="sidebar-logo">{_icon_svg("fasta")}</div>
      <div>
        <div class="sidebar-title">BioWorkbench</div>
        <div class="sidebar-subtitle">Plant genomics sequence tools</div>
      </div>
    </div>
    """


def _dashboard_hero(ready_count: int, suite_count: int) -> str:
    return f"""
    <section class="dashboard-hero">
      <div class="hero-copy">
        <div class="eyebrow">Live genomics workbench</div>
        <h1>BioWorkbench</h1>
        <p>FASTA utilities, motif discovery, ORF scanning, GC windows, k-mer ranking, and primer suggestions in one browser workspace.</p>
        <div class="hero-stats">
          <span><strong>{ready_count}</strong> ready tools</span>
          <span><strong>{suite_count}</strong> suites</span>
          <span><strong>0</strong> login required</span>
        </div>
      </div>
      <div class="hero-visual">
        <div class="sequence-board">
          <div class="board-line"><span>A</span><span>T</span><span>G</span><span>C</span><span>G</span><span>T</span><span>A</span><span>C</span></div>
          <div class="board-track"><i style="width:22%"></i><i style="width:46%"></i><i style="width:30%"></i></div>
          <div class="board-grid">
            <b>GC</b><strong>58%</strong>
            <b>ORF</b><strong>3 hits</strong>
            <b>KMER</b><strong>ATG</strong>
          </div>
        </div>
      </div>
    </section>
    """


def _badge_bar() -> str:
    return """
    <div class="badge-bar">
      <a href="https://bioworkbench-starter.streamlit.app/" target="_blank">Live demo</a>
      <a href="https://alisphd.github.io/bioworkbench-starter/" target="_blank">Project page</a>
      <a href="https://github.com/alisphd/bioworkbench-starter" target="_blank">GitHub repo</a>
      <span>Python 3.11+</span>
      <span>Streamlit</span>
      <span>PySide6 desktop</span>
    </div>
    """


def _icon_svg(name: str) -> str:
    icons = {
        "fasta": '<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M8 4h12l4 4v20H8z"/><path d="M20 4v6h6"/><path d="M12 15h8M12 19h5M12 23h8"/></svg>',
        "summary": '<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M6 25h20"/><path d="M9 22V11M16 22V6M23 22v-8"/></svg>',
        "transform": '<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M7 11h16l-4-4M23 11l-4 4"/><path d="M25 21H9l4-4M9 21l4 4"/></svg>',
        "motif": '<svg viewBox="0 0 32 32" aria-hidden="true"><circle cx="14" cy="14" r="7"/><path d="M20 20l6 6"/><path d="M10 14h8"/></svg>',
        "orf": '<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M5 9h22M5 16h22M5 23h22"/><path d="M9 9h7M14 16h10M7 23h13"/></svg>',
        "gc": '<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M5 24c5-14 9 5 13-6 3-8 6-5 9-9"/><path d="M5 27h22"/></svg>',
        "kmer": '<svg viewBox="0 0 32 32" aria-hidden="true"><rect x="5" y="6" width="8" height="8"/><rect x="19" y="6" width="8" height="8"/><rect x="5" y="19" width="8" height="8"/><rect x="19" y="19" width="8" height="8"/></svg>',
        "primer": '<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M6 11h14l-3-3M20 11l-3 3"/><path d="M26 21H12l3-3M12 21l3 3"/></svg>',
    }
    return icons.get(name, icons["fasta"])


def _inject_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --app-bg: #f5f7fb;
            --panel: #ffffff;
            --ink: #17201a;
            --muted: #5c6670;
            --line: #dbe3ea;
            --green: #0f766e;
            --blue: #2563eb;
            --amber: #b45309;
            --red: #dc2626;
        }
        .stApp {
            background: linear-gradient(180deg, #f8fafc 0%, #edf4f2 100%);
            color: var(--ink);
        }
        section[data-testid="stSidebar"] {
            background: #111827;
            border-right: 1px solid rgba(255,255,255,0.08);
        }
        section[data-testid="stSidebar"] * {
            color: #f8fafc;
        }
        .sidebar-brand {
            display: flex;
            gap: 0.75rem;
            align-items: center;
            margin: 0.35rem 0 1rem;
        }
        .sidebar-logo {
            width: 42px;
            height: 42px;
            display: grid;
            place-items: center;
            border-radius: 8px;
            background: #0f766e;
        }
        .sidebar-logo svg {
            width: 25px;
            height: 25px;
            stroke: white;
            fill: none;
            stroke-width: 2;
            stroke-linecap: round;
            stroke-linejoin: round;
        }
        .sidebar-title {
            font-size: 1.18rem;
            font-weight: 800;
        }
        .sidebar-subtitle {
            color: #b7c3cf;
            font-size: 0.82rem;
        }
        .sidebar-rule {
            border-top: 1px solid rgba(255,255,255,0.14);
            margin: 1rem 0;
        }
        .main .block-container {
            max-width: 1240px;
            padding-top: 1.4rem;
            padding-bottom: 3rem;
        }
        .dashboard-hero {
            display: grid;
            grid-template-columns: minmax(0, 1.1fr) minmax(360px, 0.9fr);
            gap: 1rem;
            align-items: stretch;
            padding: 1.1rem;
            border: 1px solid var(--line);
            border-radius: 8px;
            background: linear-gradient(135deg, #ffffff 0%, #eef8f6 54%, #eef3ff 100%);
            box-shadow: 0 18px 45px rgba(15,23,42,0.08);
        }
        .hero-copy {
            padding: 0.4rem 0.6rem;
        }
        .eyebrow {
            color: var(--green);
            font-size: 0.76rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .dashboard-hero h1 {
            margin: 0.15rem 0 0.55rem;
            color: #111827;
            font-size: 3rem;
            line-height: 1.05;
            letter-spacing: 0;
        }
        .dashboard-hero p {
            max-width: 720px;
            margin: 0;
            color: #475569;
            line-height: 1.55;
            font-size: 1rem;
        }
        .hero-stats {
            display: flex;
            flex-wrap: wrap;
            gap: 0.65rem;
            margin-top: 1.1rem;
        }
        .hero-stats span {
            display: inline-flex;
            align-items: baseline;
            gap: 0.38rem;
            padding: 0.45rem 0.65rem;
            border-radius: 7px;
            background: rgba(255,255,255,0.78);
            border: 1px solid rgba(148,163,184,0.42);
            color: #334155;
            font-weight: 650;
        }
        .hero-stats strong {
            color: #0f766e;
            font-size: 1.18rem;
        }
        .sequence-board {
            height: 100%;
            min-height: 210px;
            border-radius: 8px;
            background: #111827;
            border: 1px solid rgba(255,255,255,0.12);
            padding: 1rem;
            display: grid;
            align-content: center;
            gap: 0.85rem;
            box-shadow: inset 0 0 0 1px rgba(255,255,255,0.03);
        }
        .board-line {
            display: grid;
            grid-template-columns: repeat(8, 1fr);
            gap: 0.35rem;
        }
        .board-line span {
            display: grid;
            place-items: center;
            min-height: 34px;
            border-radius: 6px;
            background: #1f2937;
            color: #d1fae5;
            font-weight: 800;
            border: 1px solid rgba(45,212,191,0.28);
        }
        .board-track {
            display: flex;
            gap: 0.35rem;
            height: 12px;
        }
        .board-track i {
            display: block;
            border-radius: 999px;
            background: linear-gradient(90deg, #14b8a6, #60a5fa);
        }
        .board-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.5rem;
        }
        .board-grid b,
        .board-grid strong {
            display: block;
            padding: 0.35rem 0.45rem;
            border-radius: 6px;
            background: rgba(255,255,255,0.07);
            color: #e5e7eb;
        }
        .board-grid b {
            color: #94a3b8;
            font-size: 0.72rem;
            text-transform: uppercase;
        }
        .badge-bar {
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
            margin: 0.8rem 0 1rem;
        }
        .badge-bar a,
        .badge-bar span {
            display: inline-flex;
            align-items: center;
            min-height: 30px;
            padding: 0.35rem 0.62rem;
            border-radius: 6px;
            background: #111827;
            color: #ffffff !important;
            text-decoration: none;
            font-size: 0.82rem;
            font-weight: 750;
            border-left: 4px solid #0f766e;
        }
        .section-title {
            font-size: 1.02rem;
            font-weight: 850;
            margin: 1.1rem 0 0.65rem;
            color: #111827;
        }
        .tool-card {
            min-height: 252px;
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 0.95rem;
            box-shadow: 0 12px 28px rgba(15,23,42,0.06);
            border-top: 4px solid var(--accent);
        }
        .tool-card-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 0.65rem;
            margin-bottom: 0.75rem;
        }
        .tool-icon {
            width: 40px;
            height: 40px;
            display: grid;
            place-items: center;
            border-radius: 8px;
            background: color-mix(in srgb, var(--accent) 14%, white);
            border: 1px solid color-mix(in srgb, var(--accent) 26%, white);
        }
        .tool-icon svg {
            width: 24px;
            height: 24px;
            stroke: var(--accent);
            fill: none;
            stroke-width: 2;
            stroke-linecap: round;
            stroke-linejoin: round;
        }
        .tool-tag {
            color: var(--accent);
            font-size: 0.72rem;
            font-weight: 850;
            text-transform: uppercase;
            letter-spacing: 0.07em;
        }
        .tool-title {
            color: #111827;
            font-size: 1rem;
            font-weight: 850;
            line-height: 1.25;
            min-height: 2.5rem;
        }
        .tool-body {
            color: #526071;
            line-height: 1.42;
            font-size: 0.86rem;
            min-height: 4.9rem;
        }
        .tool-preview {
            height: 54px;
            margin-top: 0.75rem;
            border-radius: 7px;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            padding: 0.55rem;
            overflow: hidden;
        }
        .seq-preview,
        .kmer-preview,
        .flow-preview,
        .primer-preview {
            display: flex;
            gap: 0.35rem;
            align-items: center;
            height: 100%;
        }
        .seq-preview span,
        .kmer-preview span,
        .flow-preview span,
        .primer-preview span {
            display: grid;
            place-items: center;
            min-width: 30px;
            height: 28px;
            border-radius: 6px;
            background: color-mix(in srgb, var(--accent) 12%, white);
            color: var(--accent);
            font-size: 0.78rem;
            font-weight: 850;
        }
        .flow-preview b,
        .primer-preview b {
            width: 22px;
            height: 2px;
            background: var(--accent);
        }
        .mini-bars,
        .wave-preview {
            height: 100%;
            display: flex;
            align-items: end;
            gap: 0.36rem;
        }
        .mini-bars i,
        .wave-preview i {
            width: 18%;
            border-radius: 5px 5px 0 0;
            background: color-mix(in srgb, var(--accent) 76%, white);
        }
        .wave-preview i:nth-child(1) { height: 25%; }
        .wave-preview i:nth-child(2) { height: 72%; }
        .wave-preview i:nth-child(3) { height: 48%; }
        .wave-preview i:nth-child(4) { height: 88%; }
        .wave-preview i:nth-child(5) { height: 38%; }
        .hit-preview,
        .orf-preview {
            display: flex;
            align-items: center;
            gap: 0.2rem;
            height: 100%;
        }
        .hit-preview span,
        .orf-preview span {
            height: 8px;
            flex: 1;
            border-radius: 999px;
            background: #cbd5e1;
        }
        .hit-preview strong {
            padding: 0.2rem 0.4rem;
            border-radius: 5px;
            background: color-mix(in srgb, var(--accent) 14%, white);
            color: var(--accent);
            font-size: 0.72rem;
        }
        .orf-preview .orf-long {
            flex: 2.4;
            height: 12px;
            background: color-mix(in srgb, var(--accent) 70%, white);
        }
        .roadmap-card {
            min-height: 104px;
            background: rgba(255,255,255,0.82);
            border: 1px dashed #cbd5e1;
            border-radius: 8px;
            padding: 0.9rem;
        }
        .roadmap-tag {
            color: #64748b;
            font-size: 0.72rem;
            font-weight: 850;
            text-transform: uppercase;
            letter-spacing: 0.07em;
        }
        .roadmap-title {
            color: #111827;
            font-weight: 850;
            margin-top: 0.35rem;
        }
        .roadmap-meta {
            color: #64748b;
            margin-top: 0.4rem;
            font-size: 0.86rem;
        }
        .page-header {
            display: flex;
            gap: 0.85rem;
            align-items: center;
            border-bottom: 1px solid var(--line);
            padding-bottom: 1rem;
            margin-bottom: 1.2rem;
        }
        .page-icon {
            width: 54px;
            height: 54px;
            display: grid;
            place-items: center;
            border-radius: 8px;
            background: #e8f7f4;
            border: 1px solid #bfe3dc;
            flex: 0 0 auto;
        }
        .page-icon svg {
            width: 30px;
            height: 30px;
            stroke: #0f766e;
            fill: none;
            stroke-width: 2;
            stroke-linecap: round;
            stroke-linejoin: round;
        }
        .page-header h1 {
            color: #111827;
            font-size: 2.1rem;
            line-height: 1.08;
            margin: 0.12rem 0 0.28rem;
            letter-spacing: 0;
        }
        .page-header p {
            max-width: 760px;
            color: #526071;
            font-size: 0.98rem;
            line-height: 1.45;
            margin: 0;
        }
        div[data-testid="stMetric"] {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 0.9rem 1rem;
            box-shadow: 0 10px 24px rgba(16,24,32,0.05);
        }
        .stButton > button,
        .stDownloadButton > button,
        .stLinkButton > a {
            border-radius: 7px;
            font-weight: 760;
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
        @media (max-width: 900px) {
            .dashboard-hero {
                grid-template-columns: 1fr;
            }
            .dashboard-hero h1 {
                font-size: 2.2rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
