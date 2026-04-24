from bioworkbench.tools.fasta_formatter import format_fasta


def test_format_fasta_wraps_and_counts_records() -> None:
    result = format_fasta(">seq1\nactgactg\n>seq2\nmmkk", line_width=4, uppercase=True)

    assert result.record_count == 2
    assert result.residue_count == 12
    assert result.formatted_text == ">seq1\nACTG\nACTG\n>seq2\nMMKK"


def test_format_fasta_rejects_invalid_characters() -> None:
    try:
        format_fasta(">seq1\nACTG123")
    except ValueError as exc:
        assert "Invalid FASTA characters" in str(exc)
    else:
        raise AssertionError("Expected invalid FASTA input to raise ValueError.")

