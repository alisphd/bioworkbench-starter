from bioworkbench.tools.sequence_ops import (
    count_kmers,
    design_primers,
    find_motif_matches,
    find_orfs,
    gc_windows,
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


def test_find_orfs_reports_forward_open_reading_frames() -> None:
    records = parse_fasta(">seq1\nAAATGAAACCCGGGTAA")
    hits = find_orfs(records, min_length=12, include_reverse=False)

    assert len(hits) == 1
    assert hits[0].start == 3
    assert hits[0].end == 17
    assert hits[0].protein_sequence == "MKPG*"


def test_gc_windows_scans_with_step_size() -> None:
    records = parse_fasta(">seq1\nAAAACCCCGGGGTTTT")
    windows = gc_windows(records, window_size=8, step_size=4)

    assert [(window.start, window.end) for window in windows] == [(1, 8), (5, 12), (9, 16)]
    assert [round(window.gc_percent or 0, 2) for window in windows] == [50.0, 100.0, 50.0]


def test_count_kmers_returns_top_counts() -> None:
    records = parse_fasta(">seq1\nATATAT")
    counts = count_kmers(records, k=2, top_n=2)

    assert [(item.kmer, item.count) for item in counts] == [("AT", 3), ("TA", 2)]
