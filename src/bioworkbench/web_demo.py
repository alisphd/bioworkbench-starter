from __future__ import annotations

import streamlit as st

from bioworkbench.catalog import build_registry
from bioworkbench.tools.fasta_formatter import EXAMPLE_FASTA, format_fasta
from bioworkbench.tools.sequence_ops import design_primers, find_motif_matches, parse_fasta, summarize_records, transform_records, format_records


def render() -> None:
    st.set_page_config(
        page_title="BioWorkbench Demo",
        page_icon="🧬",
        layout="wide",
    )

    registry = build_registry()
    ready_tools = [tool for tool in registry.ready_tools()]

    st.sidebar.title("BioWorkbench Demo")
    page = st.sidebar.radio(
        "Navigate",
        [
            "Dashboard",
            "FASTA Formatter",
            "Sequence Summary",
            "Sequence Transform",
            "Motif Finder",
            "Primer Designer",
        ],
    )

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
    elif page == "Primer Designer":
        _render_primer_designer()


def _render_dashboard(registry, ready_tools) -> None:
    st.title("BioWorkbench dashboard")
    st.write(
        "This public demo exposes the ready pure-Python tools in the browser while the desktop app remains the home for heavier local integrations."
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Suites", len(registry.categories()))
    col2.metric("All tools", len(registry.all()))
    col3.metric("Ready now", len(ready_tools))

    st.subheader("Ready tools")
    for tool in ready_tools:
        with st.container(border=True):
            st.markdown(f"**{tool.name}**")
            st.write(tool.description)

    st.subheader("Planned local integrations")
    for category in registry.categories():
        with st.expander(category):
            for tool in registry.by_category(category):
                details = f"{tool.name} | {tool.status.title()}"
                if tool.external_tools:
                    details += f" | Uses {', '.join(tool.external_tools)}"
                st.write(details)


def _render_fasta_formatter() -> None:
    st.title("FASTA Formatter")
    left, right = st.columns([2, 1])
    with right:
        line_width = st.number_input("Wrap width", min_value=10, max_value=200, value=60)
        uppercase = st.checkbox("Uppercase sequence", value=True)
    with left:
        fasta_text = st.text_area("Input FASTA", value=EXAMPLE_FASTA, height=280)

    if st.button("Format FASTA", type="primary"):
        try:
            result = format_fasta(fasta_text, line_width=int(line_width), uppercase=uppercase)
            st.success(f"Formatted {result.record_count} record(s) across {result.residue_count} residues.")
            st.code(result.formatted_text, language="text")
        except ValueError as exc:
            st.error(str(exc))


def _render_sequence_summary() -> None:
    st.title("Sequence Summary")
    fasta_text = st.text_area("Input FASTA", value=EXAMPLE_FASTA, height=280)
    if st.button("Summarize sequences", type="primary"):
        try:
            summaries = summarize_records(parse_fasta(fasta_text, uppercase=True))
            st.success(f"Summarized {len(summaries)} record(s).")
            for item in summaries:
                gc_text = "n/a" if item.gc_percent is None else f"{item.gc_percent:.2f}%"
                st.markdown(
                    f"**{item.header}**  \n"
                    f"Type: {item.sequence_type}  \n"
                    f"Length: {item.length}  \n"
                    f"GC: {gc_text}  \n"
                    f"Ambiguous Ns: {item.ambiguous_count}  \n"
                    f"Preview: `{item.preview or '(empty)'}`"
                )
        except ValueError as exc:
            st.error(str(exc))


def _render_sequence_transform() -> None:
    st.title("Sequence Transform")
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
        fasta_text = st.text_area("Input FASTA", value=EXAMPLE_FASTA, height=280)
    with right:
        mode_label = st.selectbox("Transform", list(options.keys()))
        frame = st.number_input("Frame", min_value=1, max_value=3, value=1, disabled=mode_label != "Translate")
        line_width = st.number_input("Wrap width", min_value=10, max_value=200, value=60)

    if st.button("Apply transform", type="primary"):
        try:
            records = parse_fasta(fasta_text, uppercase=True)
            transformed = transform_records(records, options[mode_label], frame=int(frame))
            st.success(f"Transformed {len(transformed)} record(s).")
            st.code(format_records(transformed, line_width=int(line_width)), language="text")
        except ValueError as exc:
            st.error(str(exc))


def _render_motif_finder() -> None:
    st.title("Motif Finder")
    fasta_text = st.text_area("Input FASTA", value=EXAMPLE_FASTA, height=280)
    col1, col2 = st.columns([2, 1])
    with col1:
        motif = st.text_input("Motif", value="ATG")
    with col2:
        case_sensitive = st.checkbox("Case sensitive", value=False)

    if st.button("Find motif", type="primary"):
        try:
            matches = find_motif_matches(parse_fasta(fasta_text, uppercase=True), motif, case_sensitive=case_sensitive)
            if not matches:
                st.info("No matches found.")
                return
            st.success(f"Found {len(matches)} match(es).")
            for match in matches:
                st.write(f"{match.header}: {match.matched_text} at {match.start}-{match.end}")
        except ValueError as exc:
            st.error(str(exc))


def _render_primer_designer() -> None:
    st.title("Primer Designer")
    fasta_text = st.text_area("Input nucleotide FASTA", value=EXAMPLE_FASTA, height=280)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        primer_length = st.number_input("Primer length", min_value=16, max_value=30, value=20)
    with col2:
        min_gc = st.number_input("Min GC", min_value=0.0, max_value=100.0, value=40.0)
    with col3:
        max_gc = st.number_input("Max GC", min_value=0.0, max_value=100.0, value=60.0)
    with col4:
        top_n = st.number_input("Top N", min_value=1, max_value=20, value=5)

    if st.button("Suggest primers", type="primary"):
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
            st.success(
                f"Scanned {result.scanned_records} nucleotide record(s) and returned "
                f"{len(result.forward)} forward plus {len(result.reverse)} reverse candidates."
            )
            st.markdown("**Forward candidates**")
            for candidate in result.forward:
                st.write(
                    f"{candidate.header} | {candidate.sequence} | {candidate.start}-{candidate.end} | "
                    f"GC {candidate.gc_percent:.2f}% | Tm {candidate.tm_celsius:.1f} C"
                )
            st.markdown("**Reverse candidates**")
            for candidate in result.reverse:
                st.write(
                    f"{candidate.header} | {candidate.sequence} | {candidate.start}-{candidate.end} | "
                    f"GC {candidate.gc_percent:.2f}% | Tm {candidate.tm_celsius:.1f} C"
                )
        except ValueError as exc:
            st.error(str(exc))

