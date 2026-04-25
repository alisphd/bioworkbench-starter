from __future__ import annotations

from dataclasses import dataclass
from collections import Counter


DNA_ALPHABET = set("ACGTN")
RNA_ALPHABET = set("ACGUN")
PROTEIN_ALPHABET = set("ABCDEFGHIKLMNPQRSTVWXYZ*.-")
FASTA_ALLOWED = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz*.-")
CODON_TABLE = {
    "TTT": "F",
    "TTC": "F",
    "TTA": "L",
    "TTG": "L",
    "CTT": "L",
    "CTC": "L",
    "CTA": "L",
    "CTG": "L",
    "ATT": "I",
    "ATC": "I",
    "ATA": "I",
    "ATG": "M",
    "GTT": "V",
    "GTC": "V",
    "GTA": "V",
    "GTG": "V",
    "TCT": "S",
    "TCC": "S",
    "TCA": "S",
    "TCG": "S",
    "CCT": "P",
    "CCC": "P",
    "CCA": "P",
    "CCG": "P",
    "ACT": "T",
    "ACC": "T",
    "ACA": "T",
    "ACG": "T",
    "GCT": "A",
    "GCC": "A",
    "GCA": "A",
    "GCG": "A",
    "TAT": "Y",
    "TAC": "Y",
    "TAA": "*",
    "TAG": "*",
    "CAT": "H",
    "CAC": "H",
    "CAA": "Q",
    "CAG": "Q",
    "AAT": "N",
    "AAC": "N",
    "AAA": "K",
    "AAG": "K",
    "GAT": "D",
    "GAC": "D",
    "GAA": "E",
    "GAG": "E",
    "TGT": "C",
    "TGC": "C",
    "TGA": "*",
    "TGG": "W",
    "CGT": "R",
    "CGC": "R",
    "CGA": "R",
    "CGG": "R",
    "AGT": "S",
    "AGC": "S",
    "AGA": "R",
    "AGG": "R",
    "GGT": "G",
    "GGC": "G",
    "GGA": "G",
    "GGG": "G",
}
COMPLEMENT_TABLE = str.maketrans(
    {
        "A": "T",
        "C": "G",
        "G": "C",
        "T": "A",
        "U": "A",
        "N": "N",
    }
)


@dataclass(frozen=True)
class SequenceRecord:
    header: str
    sequence: str


@dataclass(frozen=True)
class SequenceSummary:
    header: str
    sequence_type: str
    length: int
    gc_percent: float | None
    ambiguous_count: int
    preview: str


@dataclass(frozen=True)
class MotifMatch:
    header: str
    start: int
    end: int
    matched_text: str


@dataclass(frozen=True)
class PrimerCandidate:
    header: str
    direction: str
    start: int
    end: int
    sequence: str
    gc_percent: float
    tm_celsius: float
    score: float


@dataclass(frozen=True)
class PrimerDesignResult:
    forward: tuple[PrimerCandidate, ...]
    reverse: tuple[PrimerCandidate, ...]
    scanned_records: int


@dataclass(frozen=True)
class OrfHit:
    header: str
    frame: int
    start: int
    end: int
    length: int
    nucleotide_sequence: str
    protein_sequence: str


@dataclass(frozen=True)
class GcWindow:
    header: str
    start: int
    end: int
    gc_percent: float | None


@dataclass(frozen=True)
class KmerCount:
    kmer: str
    count: int
    frequency_percent: float


def parse_fasta(text: str, uppercase: bool = True) -> list[SequenceRecord]:
    records: list[SequenceRecord] = []
    current_header: str | None = None
    current_sequence_parts: list[str] = []

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith(">"):
            if current_header is not None:
                records.append(SequenceRecord(current_header, "".join(current_sequence_parts)))
            current_header = line[1:].strip() or f"unnamed_record_{len(records) + 1}"
            current_sequence_parts = []
            continue

        if current_header is None:
            raise ValueError("FASTA content must start with a header line that begins with '>'.")

        cleaned = "".join(character for character in line if not character.isspace())
        invalid = sorted({character for character in cleaned if character not in FASTA_ALLOWED})
        if invalid:
            joined = ", ".join(invalid)
            raise ValueError(f"Invalid FASTA characters on line {line_number}: {joined}")

        current_sequence_parts.append(cleaned.upper() if uppercase else cleaned)

    if current_header is not None:
        records.append(SequenceRecord(current_header, "".join(current_sequence_parts)))

    if not records:
        raise ValueError("No FASTA records found.")

    return records


def format_records(records: list[SequenceRecord], line_width: int = 60) -> str:
    if line_width < 1:
        raise ValueError("Line width must be at least 1.")

    lines: list[str] = []
    for record in records:
        lines.append(f">{record.header}")
        lines.extend(wrap_sequence(record.sequence, line_width))
    return "\n".join(lines)


def wrap_sequence(sequence: str, line_width: int) -> list[str]:
    return [sequence[index : index + line_width] for index in range(0, len(sequence), line_width)] or [""]


def infer_sequence_type(sequence: str) -> str:
    residue_set = {char for char in sequence.upper() if char.isalpha()}
    if not residue_set:
        return "Unknown"
    if residue_set <= DNA_ALPHABET:
        return "DNA"
    if residue_set <= RNA_ALPHABET:
        return "RNA"
    if residue_set <= (DNA_ALPHABET | RNA_ALPHABET):
        return "Nucleotide"
    if residue_set <= PROTEIN_ALPHABET:
        return "Protein"
    return "Mixed"


def gc_content(sequence: str) -> float | None:
    clean = [char for char in sequence.upper() if char in {"A", "C", "G", "T", "U"}]
    if not clean:
        return None
    gc_count = sum(1 for char in clean if char in {"G", "C"})
    return (gc_count / len(clean)) * 100


def summarize_records(records: list[SequenceRecord]) -> list[SequenceSummary]:
    summaries: list[SequenceSummary] = []
    for record in records:
        summaries.append(
            SequenceSummary(
                header=record.header,
                sequence_type=infer_sequence_type(record.sequence),
                length=len(record.sequence),
                gc_percent=gc_content(record.sequence),
                ambiguous_count=sum(1 for char in record.sequence.upper() if char == "N"),
                preview=record.sequence[:24] + ("..." if len(record.sequence) > 24 else ""),
            )
        )
    return summaries


def reverse_complement(sequence: str) -> str:
    return sequence.upper().translate(COMPLEMENT_TABLE)[::-1]


def translate_sequence(sequence: str, frame: int = 1) -> str:
    if frame not in {1, 2, 3}:
        raise ValueError("Translation frame must be 1, 2, or 3.")

    clean = "".join(char for char in sequence.upper().replace("U", "T") if char.isalpha())
    amino_acids: list[str] = []
    for index in range(frame - 1, len(clean) - 2, 3):
        codon = clean[index : index + 3]
        amino_acids.append(CODON_TABLE.get(codon, "X"))
    return "".join(amino_acids)


def transform_records(records: list[SequenceRecord], mode: str, frame: int = 1) -> list[SequenceRecord]:
    transformed: list[SequenceRecord] = []
    for record in records:
        if mode == "uppercase":
            sequence = record.sequence.upper()
        elif mode == "reverse":
            sequence = record.sequence[::-1]
        elif mode == "reverse_complement":
            sequence = reverse_complement(record.sequence)
        elif mode == "dna_to_rna":
            sequence = record.sequence.upper().replace("T", "U")
        elif mode == "rna_to_dna":
            sequence = record.sequence.upper().replace("U", "T")
        elif mode == "translate":
            sequence = translate_sequence(record.sequence, frame=frame)
        else:
            raise ValueError(f"Unsupported transform mode: {mode}")

        suffix = {
            "uppercase": "UPPER",
            "reverse": "REVERSE",
            "reverse_complement": "REVCOMP",
            "dna_to_rna": "RNA",
            "rna_to_dna": "DNA",
            "translate": f"FRAME{frame}",
        }[mode]
        transformed.append(SequenceRecord(f"{record.header} | {suffix}", sequence))
    return transformed


def find_motif_matches(
    records: list[SequenceRecord],
    motif: str,
    case_sensitive: bool = False,
) -> list[MotifMatch]:
    motif_text = motif.strip()
    if not motif_text:
        raise ValueError("Motif cannot be empty.")

    search_motif = motif_text if case_sensitive else motif_text.upper()
    matches: list[MotifMatch] = []

    for record in records:
        haystack = record.sequence if case_sensitive else record.sequence.upper()
        start = 0
        while True:
            index = haystack.find(search_motif, start)
            if index == -1:
                break
            matches.append(
                MotifMatch(
                    header=record.header,
                    start=index + 1,
                    end=index + len(search_motif),
                    matched_text=record.sequence[index : index + len(search_motif)],
                )
            )
            start = index + 1
    return matches


def design_primers(
    records: list[SequenceRecord],
    primer_length: int = 20,
    min_gc: float = 40.0,
    max_gc: float = 60.0,
    top_n: int = 5,
) -> PrimerDesignResult:
    if primer_length < 10:
        raise ValueError("Primer length must be at least 10.")
    if min_gc > max_gc:
        raise ValueError("Minimum GC cannot be greater than maximum GC.")
    if top_n < 1:
        raise ValueError("Top N must be at least 1.")

    forward_candidates: list[PrimerCandidate] = []
    reverse_candidates: list[PrimerCandidate] = []
    scanned_records = 0

    for record in records:
        sequence_type = infer_sequence_type(record.sequence)
        if sequence_type not in {"DNA", "RNA", "Nucleotide"}:
            continue

        normalized = record.sequence.upper().replace("U", "T")
        scanned_records += 1

        for index in range(0, len(normalized) - primer_length + 1):
            window = normalized[index : index + primer_length]
            if set(window) - {"A", "C", "G", "T"}:
                continue
            if _has_homopolymer_run(window, 5):
                continue

            gc_percent = gc_content(window)
            if gc_percent is None or gc_percent < min_gc or gc_percent > max_gc:
                continue

            tm_celsius = _wallace_tm(window)
            score = abs(gc_percent - 50.0) + abs(tm_celsius - 60.0) / 2.0

            forward_candidates.append(
                PrimerCandidate(
                    header=record.header,
                    direction="Forward",
                    start=index + 1,
                    end=index + primer_length,
                    sequence=window,
                    gc_percent=gc_percent,
                    tm_celsius=tm_celsius,
                    score=score,
                )
            )
            reverse_candidates.append(
                PrimerCandidate(
                    header=record.header,
                    direction="Reverse",
                    start=index + 1,
                    end=index + primer_length,
                    sequence=reverse_complement(window),
                    gc_percent=gc_percent,
                    tm_celsius=tm_celsius,
                    score=score,
                )
            )

    forward_sorted = tuple(sorted(forward_candidates, key=_primer_sort_key)[:top_n])
    reverse_sorted = tuple(sorted(reverse_candidates, key=_primer_sort_key)[:top_n])
    return PrimerDesignResult(forward=forward_sorted, reverse=reverse_sorted, scanned_records=scanned_records)


def find_orfs(
    records: list[SequenceRecord],
    min_length: int = 90,
    include_reverse: bool = True,
) -> list[OrfHit]:
    if min_length < 3:
        raise ValueError("Minimum ORF length must be at least 3.")

    hits: list[OrfHit] = []
    stop_codons = {"TAA", "TAG", "TGA"}

    for record in records:
        if infer_sequence_type(record.sequence) not in {"DNA", "RNA", "Nucleotide"}:
            continue

        forward_sequence = _normalize_nucleotide(record.sequence)
        search_targets = [(1, forward_sequence)]
        if include_reverse:
            search_targets.append((-1, reverse_complement(forward_sequence)))

        for direction, sequence in search_targets:
            for frame_offset in range(3):
                index = frame_offset
                while index <= len(sequence) - 3:
                    codon = sequence[index : index + 3]
                    if codon != "ATG":
                        index += 3
                        continue

                    stop_index = index + 3
                    while stop_index <= len(sequence) - 3:
                        stop_codon = sequence[stop_index : stop_index + 3]
                        if stop_codon in stop_codons:
                            end = stop_index + 3
                            nucleotide_sequence = sequence[index:end]
                            if len(nucleotide_sequence) >= min_length:
                                start_position, end_position = _project_orf_coordinates(
                                    index,
                                    end,
                                    len(sequence),
                                    direction,
                                )
                                hits.append(
                                    OrfHit(
                                        header=record.header,
                                        frame=frame_offset + 1 if direction == 1 else -(frame_offset + 1),
                                        start=start_position,
                                        end=end_position,
                                        length=len(nucleotide_sequence),
                                        nucleotide_sequence=nucleotide_sequence,
                                        protein_sequence=translate_sequence(nucleotide_sequence),
                                    )
                                )
                            index = stop_index + 3
                            break
                        stop_index += 3
                    else:
                        index += 3

    return sorted(hits, key=lambda hit: (hit.header, hit.start, -hit.length))


def gc_windows(
    records: list[SequenceRecord],
    window_size: int = 100,
    step_size: int = 50,
) -> list[GcWindow]:
    if window_size < 1:
        raise ValueError("Window size must be at least 1.")
    if step_size < 1:
        raise ValueError("Step size must be at least 1.")

    windows: list[GcWindow] = []
    for record in records:
        if infer_sequence_type(record.sequence) not in {"DNA", "RNA", "Nucleotide"}:
            continue

        sequence = _normalize_nucleotide(record.sequence)
        if not sequence:
            continue

        if len(sequence) <= window_size:
            windows.append(GcWindow(record.header, 1, len(sequence), gc_content(sequence)))
            continue

        for start_index in range(0, len(sequence) - window_size + 1, step_size):
            window = sequence[start_index : start_index + window_size]
            windows.append(
                GcWindow(
                    header=record.header,
                    start=start_index + 1,
                    end=start_index + window_size,
                    gc_percent=gc_content(window),
                )
            )
    return windows


def count_kmers(
    records: list[SequenceRecord],
    k: int = 3,
    top_n: int = 20,
    nucleotide_only: bool = True,
) -> list[KmerCount]:
    if k < 1:
        raise ValueError("K-mer size must be at least 1.")
    if top_n < 1:
        raise ValueError("Top N must be at least 1.")

    counter: Counter[str] = Counter()
    total = 0
    allowed = {"A", "C", "G", "T", "U", "N"}

    for record in records:
        sequence = record.sequence.upper()
        if nucleotide_only:
            sequence = sequence.replace("U", "T")
        for index in range(0, len(sequence) - k + 1):
            kmer = sequence[index : index + k]
            if nucleotide_only and set(kmer) - allowed:
                continue
            if not kmer.isalpha():
                continue
            counter[kmer] += 1
            total += 1

    if total == 0:
        return []

    return [
        KmerCount(kmer=kmer, count=count, frequency_percent=(count / total) * 100)
        for kmer, count in counter.most_common(top_n)
    ]


def _normalize_nucleotide(sequence: str) -> str:
    return "".join(char for char in sequence.upper().replace("U", "T") if char.isalpha())


def _project_orf_coordinates(start: int, end: int, sequence_length: int, direction: int) -> tuple[int, int]:
    if direction == 1:
        return start + 1, end
    return sequence_length - end + 1, sequence_length - start


def _has_homopolymer_run(sequence: str, max_run: int) -> bool:
    current = 1
    for index in range(1, len(sequence)):
        if sequence[index] == sequence[index - 1]:
            current += 1
            if current >= max_run:
                return True
        else:
            current = 1
    return False


def _wallace_tm(sequence: str) -> float:
    at_count = sum(1 for char in sequence if char in {"A", "T"})
    gc_count = sum(1 for char in sequence if char in {"G", "C"})
    return float((2 * at_count) + (4 * gc_count))


def _primer_sort_key(candidate: PrimerCandidate) -> tuple[float, str, int]:
    return (candidate.score, candidate.header, candidate.start)
