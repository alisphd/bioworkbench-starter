from bioworkbench.tools.sequence_ops import (
    design_primers,
    find_motif_matches,
    parse_fasta,
    summarize_records,
    transform_records,
)


def test_sequence_summary_reports_type_and_length() -> None:
    records = parse_fasta(">seq1\nATGCATGC\n>seq2\nMKTW")
    summaries = summarize_records(records)

    assert summaries[0].sequence_type == "DNA"
    assert summaries[0].length == 8
    assert summaries[1].sequence_type == "Protein"


def test_transform_records_reverse_complement_and_translate() -> None:
    records = parse_fasta(">seq1\nATGGCC")
    revcomp = transform_records(records, "reverse_complement")
    translated = transform_records(records, "translate", frame=1)

    assert revcomp[0].sequence == "GGCCAT"
    assert translated[0].sequence == "MA"


def test_find_motif_matches_reports_overlapping_hits() -> None:
    records = parse_fasta(">seq1\nATATAT")
    matches = find_motif_matches(records, "ATA")

    assert [(match.start, match.end) for match in matches] == [(1, 3), (3, 5)]


def test_design_primers_returns_ranked_candidates() -> None:
    records = parse_fasta(">seq1\nATGCGTACGTAGCTAGCTAGCTAGCTAACGTTAGC")
    result = design_primers(records, primer_length=18, min_gc=40.0, max_gc=70.0, top_n=3)

    assert result.scanned_records == 1
    assert len(result.forward) == 3
    assert len(result.reverse) == 3
