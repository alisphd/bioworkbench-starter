from __future__ import annotations

from dataclasses import dataclass

from bioworkbench.tools.sequence_ops import format_records, parse_fasta


EXAMPLE_FASTA = """>Arabidopsis_geneA
ATGCGTACGTAGCTAGCTAGCTAGCTAACGTTAGC
>Arabidopsis_geneB
ATGGGCTTACCGATGATGCTAGCTAGGCTTACCAA
>Vigna_gene7
ATGAACGGTGCTGCTGATGCTTTCGATCGATCGTA
"""


@dataclass(frozen=True)
class FastaFormatResult:
    formatted_text: str
    record_count: int
    residue_count: int
    warnings: tuple[str, ...] = ()


def format_fasta(text: str, line_width: int = 60, uppercase: bool = True) -> FastaFormatResult:
    if line_width < 1:
        raise ValueError("Line width must be at least 1.")

    records = parse_fasta(text, uppercase=uppercase)

    warnings: list[str] = []
    residue_count = 0

    for record in records:
        if not record.sequence:
            warnings.append(f"{record.header} has no sequence data.")
            continue

        residue_count += len(record.sequence)

    return FastaFormatResult(
        formatted_text=format_records(records, line_width=line_width),
        record_count=len(records),
        residue_count=residue_count,
        warnings=tuple(warnings),
    )
