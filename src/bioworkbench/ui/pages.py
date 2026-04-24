from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from bioworkbench.core.models import ToolSpec
from bioworkbench.core.registry import ToolRegistry
from bioworkbench.tools.fasta_formatter import EXAMPLE_FASTA, format_fasta
from bioworkbench.tools.sequence_ops import (
    PrimerDesignResult,
    design_primers,
    find_motif_matches,
    format_records,
    parse_fasta,
    summarize_records,
    transform_records,
)


def make_card() -> QFrame:
    card = QFrame()
    card.setObjectName("Card")
    return card


def make_badge(text: str, ready: bool) -> QLabel:
    badge = QLabel(text)
    badge.setObjectName("BadgeReady" if ready else "BadgePlanned")
    badge.setAlignment(Qt.AlignCenter)
    return badge


class DashboardPage(QWidget):
    def __init__(self, registry: ToolRegistry, launch_tool: Callable[[str], None]) -> None:
        super().__init__()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()
        outer = QVBoxLayout(content)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(18)

        hero = make_card()
        hero_layout = QVBoxLayout(hero)
        title = QLabel("BioWorkbench dashboard")
        title.setObjectName("HeroTitle")
        subtitle = QLabel(
            "Use the ready tools now, keep the planned modules visible, and ship both a desktop app and a browser-based demo from the same core sequence logic."
        )
        subtitle.setWordWrap(True)
        subtitle.setObjectName("HeroBody")
        hero_layout.addWidget(title)
        hero_layout.addWidget(subtitle)
        outer.addWidget(hero)

        stats = QHBoxLayout()
        stats.setSpacing(16)
        stats.addWidget(_make_stat_card("Suites", str(len(registry.categories()))))
        stats.addWidget(_make_stat_card("All Tools", str(len(registry.all()))))
        stats.addWidget(_make_stat_card("Ready Now", str(len(registry.ready_tools()))))
        outer.addLayout(stats)

        ready_card = make_card()
        ready_layout = QVBoxLayout(ready_card)
        ready_title = QLabel("Try these tools now")
        ready_title.setObjectName("SectionTitle")
        ready_layout.addWidget(ready_title)

        ready_grid = QGridLayout()
        ready_grid.setHorizontalSpacing(16)
        ready_grid.setVerticalSpacing(16)
        for index, tool in enumerate(registry.ready_tools()):
            ready_grid.addWidget(_make_tool_launch_card(tool, launch_tool), index // 2, index % 2)
        ready_layout.addLayout(ready_grid)
        outer.addWidget(ready_card)

        roadmap = QGridLayout()
        roadmap.setHorizontalSpacing(16)
        roadmap.setVerticalSpacing(16)
        for index, category in enumerate(registry.categories()):
            group = QGroupBox(category)
            group.setObjectName("ToolGroup")
            group_layout = QVBoxLayout(group)
            for tool in registry.by_category(category):
                text = f"{tool.name} | {tool.status.title()}"
                if tool.external_tools:
                    text += f" | Uses {', '.join(tool.external_tools)}"
                label = QLabel(text)
                label.setWordWrap(True)
                group_layout.addWidget(label)
            roadmap.addWidget(group, index // 2, index % 2)

        roadmap_card = make_card()
        roadmap_layout = QVBoxLayout(roadmap_card)
        roadmap_title = QLabel("Current roadmap")
        roadmap_title.setObjectName("SectionTitle")
        roadmap_note = QLabel(
            "The dashboard shows which modules are already interactive and which ones are queued for external-tool integration."
        )
        roadmap_note.setWordWrap(True)
        roadmap_layout.addWidget(roadmap_title)
        roadmap_layout.addWidget(roadmap_note)
        roadmap_layout.addLayout(roadmap)
        outer.addWidget(roadmap_card)

        deploy_card = make_card()
        deploy_layout = QVBoxLayout(deploy_card)
        deploy_title = QLabel("Publishing path")
        deploy_title.setObjectName("SectionTitle")
        deploy_body = QLabel(
            "Keep the full desktop app for local/offline work. Use the included Streamlit demo to let people test the ready tools online before you wire in heavy local binaries."
        )
        deploy_body.setWordWrap(True)
        deploy_layout.addWidget(deploy_title)
        deploy_layout.addWidget(deploy_body)
        outer.addWidget(deploy_card)
        outer.addStretch(1)

        scroll.setWidget(content)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)


class PlaceholderToolPage(QWidget):
    def __init__(self, tool: ToolSpec) -> None:
        super().__init__()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        hero = make_card()
        hero_layout = QVBoxLayout(hero)
        header = QHBoxLayout()
        title = QLabel(tool.name)
        title.setObjectName("HeroTitle")
        header.addWidget(title, 1)
        header.addWidget(make_badge(tool.status.title(), tool.is_ready))
        description = QLabel(tool.description)
        description.setWordWrap(True)
        description.setObjectName("HeroBody")
        hero_layout.addLayout(header)
        hero_layout.addWidget(description)
        layout.addWidget(hero)

        if tool.external_tools:
            ext_card = make_card()
            ext_layout = QVBoxLayout(ext_card)
            ext_title = QLabel("External tools you will likely wrap")
            ext_title.setObjectName("SectionTitle")
            ext_value = QLabel(", ".join(tool.external_tools))
            ext_value.setWordWrap(True)
            ext_layout.addWidget(ext_title)
            ext_layout.addWidget(ext_value)
            layout.addWidget(ext_card)

        steps_card = make_card()
        steps_layout = QVBoxLayout(steps_card)
        steps_title = QLabel("Next implementation steps")
        steps_title.setObjectName("SectionTitle")
        steps_layout.addWidget(steps_title)
        for item in tool.next_steps or ("Sketch the inputs and outputs for this workflow.",):
            bullet = QLabel(f"- {item}")
            bullet.setWordWrap(True)
            steps_layout.addWidget(bullet)
        layout.addWidget(steps_card)
        layout.addStretch(1)

        scroll.setWidget(content)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(scroll)


class FastaFormatterPage(QWidget):
    def __init__(self, tool: ToolSpec) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        layout.addWidget(_build_page_header(tool))

        controls = make_card()
        controls_layout = QHBoxLayout(controls)
        controls_layout.setSpacing(14)

        width_label = QLabel("Wrap width")
        self.line_width = QSpinBox()
        self.line_width.setRange(10, 200)
        self.line_width.setValue(60)

        self.uppercase = QCheckBox("Uppercase sequence")
        self.uppercase.setChecked(True)

        format_button = QPushButton("Format FASTA")
        format_button.clicked.connect(self._format_sequences)

        example_button = QPushButton("Load Example")
        example_button.setObjectName("SecondaryButton")
        example_button.clicked.connect(self._load_example)

        clear_button = QPushButton("Clear")
        clear_button.setObjectName("SecondaryButton")
        clear_button.clicked.connect(self._clear_all)

        controls_layout.addWidget(width_label)
        controls_layout.addWidget(self.line_width)
        controls_layout.addWidget(self.uppercase)
        controls_layout.addStretch(1)
        controls_layout.addWidget(example_button)
        controls_layout.addWidget(clear_button)
        controls_layout.addWidget(format_button)
        layout.addWidget(controls)

        self.input_box, self.output_box = _add_side_by_side_editors(
            layout,
            "Input FASTA",
            "Paste FASTA records here...",
            "Formatted FASTA",
            "Formatted FASTA will appear here.",
        )

        self.summary = QLabel("Load the example or paste your own FASTA to begin.")
        self.summary.setWordWrap(True)
        self.summary.setObjectName("StatusLabel")
        layout.addWidget(self.summary)

    def _clear_all(self) -> None:
        self.input_box.clear()
        self.output_box.clear()
        self.summary.setText("Cleared. Paste FASTA content to format it again.")

    def _load_example(self) -> None:
        self.input_box.setPlainText(EXAMPLE_FASTA.strip())
        self._format_sequences()

    def _format_sequences(self) -> None:
        try:
            result = format_fasta(
                self.input_box.toPlainText(),
                line_width=self.line_width.value(),
                uppercase=self.uppercase.isChecked(),
            )
        except ValueError as exc:
            self.output_box.clear()
            self.summary.setText(f"Validation error: {exc}")
            return

        self.output_box.setPlainText(result.formatted_text)
        message = f"Formatted {result.record_count} record(s) across {result.residue_count} residues."
        if result.warnings:
            message += " Warnings: " + " | ".join(result.warnings)
        self.summary.setText(message)


class SequenceSummaryPage(QWidget):
    def __init__(self, tool: ToolSpec) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        layout.addWidget(_build_page_header(tool))
        layout.addWidget(_build_standard_actions(self._load_example, self._clear_all, self._summarize))

        self.input_box, self.output_box = _add_side_by_side_editors(
            layout,
            "Input FASTA",
            "Paste FASTA records here...",
            "Summary Report",
            "Summary statistics will appear here.",
            read_only_output=True,
        )

        self.summary = QLabel("Summaries include record count, sequence type, GC content, and ambiguity counts.")
        self.summary.setWordWrap(True)
        self.summary.setObjectName("StatusLabel")
        layout.addWidget(self.summary)

    def _load_example(self) -> None:
        self.input_box.setPlainText(EXAMPLE_FASTA.strip())
        self._summarize()

    def _clear_all(self) -> None:
        self.input_box.clear()
        self.output_box.clear()
        self.summary.setText("Cleared. Paste FASTA content to inspect it again.")

    def _summarize(self) -> None:
        try:
            records = parse_fasta(self.input_box.toPlainText(), uppercase=True)
            summaries = summarize_records(records)
        except ValueError as exc:
            self.output_box.clear()
            self.summary.setText(f"Validation error: {exc}")
            return

        total_residues = sum(item.length for item in summaries)
        lines = [
            "Dataset summary",
            f"- Records: {len(summaries)}",
            f"- Total residues: {total_residues}",
            "",
            "Per-record details",
        ]

        for item in summaries:
            gc_text = "n/a" if item.gc_percent is None else f"{item.gc_percent:.2f}%"
            lines.extend(
                [
                    f"[{item.header}]",
                    f"Type: {item.sequence_type}",
                    f"Length: {item.length}",
                    f"GC: {gc_text}",
                    f"Ambiguous Ns: {item.ambiguous_count}",
                    f"Preview: {item.preview or '(empty)'}",
                    "",
                ]
            )

        self.output_box.setPlainText("\n".join(lines).strip())
        self.summary.setText(f"Summarized {len(summaries)} record(s) across {total_residues} residues.")


class SequenceTransformPage(QWidget):
    def __init__(self, tool: ToolSpec) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        layout.addWidget(_build_page_header(tool))

        controls = make_card()
        controls_layout = QHBoxLayout(controls)
        controls_layout.setSpacing(14)

        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Uppercase", "uppercase")
        self.mode_combo.addItem("Reverse", "reverse")
        self.mode_combo.addItem("Reverse complement", "reverse_complement")
        self.mode_combo.addItem("DNA to RNA", "dna_to_rna")
        self.mode_combo.addItem("RNA to DNA", "rna_to_dna")
        self.mode_combo.addItem("Translate", "translate")

        self.frame_selector = QSpinBox()
        self.frame_selector.setRange(1, 3)
        self.frame_selector.setValue(1)

        self.line_width = QSpinBox()
        self.line_width.setRange(10, 200)
        self.line_width.setValue(60)

        self.mode_combo.currentIndexChanged.connect(self._sync_frame_state)

        controls_layout.addWidget(QLabel("Transform"))
        controls_layout.addWidget(self.mode_combo)
        controls_layout.addWidget(QLabel("Frame"))
        controls_layout.addWidget(self.frame_selector)
        controls_layout.addWidget(QLabel("Wrap width"))
        controls_layout.addWidget(self.line_width)
        controls_layout.addStretch(1)

        example_button = QPushButton("Load Example")
        example_button.setObjectName("SecondaryButton")
        example_button.clicked.connect(self._load_example)
        clear_button = QPushButton("Clear")
        clear_button.setObjectName("SecondaryButton")
        clear_button.clicked.connect(self._clear_all)
        apply_button = QPushButton("Apply Transform")
        apply_button.clicked.connect(self._transform)

        controls_layout.addWidget(example_button)
        controls_layout.addWidget(clear_button)
        controls_layout.addWidget(apply_button)
        layout.addWidget(controls)

        self.input_box, self.output_box = _add_side_by_side_editors(
            layout,
            "Input FASTA",
            "Paste FASTA records here...",
            "Transformed Output",
            "Transformed FASTA will appear here.",
            read_only_output=True,
        )

        self.summary = QLabel("Choose a transform and apply it to one or more FASTA records.")
        self.summary.setWordWrap(True)
        self.summary.setObjectName("StatusLabel")
        layout.addWidget(self.summary)
        self._sync_frame_state()

    def _sync_frame_state(self) -> None:
        self.frame_selector.setEnabled(self.mode_combo.currentData() == "translate")

    def _load_example(self) -> None:
        self.input_box.setPlainText(EXAMPLE_FASTA.strip())
        self._transform()

    def _clear_all(self) -> None:
        self.input_box.clear()
        self.output_box.clear()
        self.summary.setText("Cleared. Paste FASTA content to transform it again.")

    def _transform(self) -> None:
        try:
            records = parse_fasta(self.input_box.toPlainText(), uppercase=True)
            transformed = transform_records(
                records,
                self.mode_combo.currentData(),
                frame=self.frame_selector.value(),
            )
            output = format_records(transformed, line_width=self.line_width.value())
        except ValueError as exc:
            self.output_box.clear()
            self.summary.setText(f"Validation error: {exc}")
            return

        self.output_box.setPlainText(output)
        self.summary.setText(
            f"Transformed {len(transformed)} record(s) using {self.mode_combo.currentText().lower()}."
        )


class MotifFinderPage(QWidget):
    def __init__(self, tool: ToolSpec) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        layout.addWidget(_build_page_header(tool))

        controls = make_card()
        controls_layout = QHBoxLayout(controls)
        controls_layout.setSpacing(14)

        self.motif_input = QLineEdit()
        self.motif_input.setPlaceholderText("Example: ATG")
        self.case_sensitive = QCheckBox("Case sensitive")

        example_button = QPushButton("Load Example")
        example_button.setObjectName("SecondaryButton")
        example_button.clicked.connect(self._load_example)
        clear_button = QPushButton("Clear")
        clear_button.setObjectName("SecondaryButton")
        clear_button.clicked.connect(self._clear_all)
        find_button = QPushButton("Find Motif")
        find_button.clicked.connect(self._scan)

        controls_layout.addWidget(QLabel("Motif"))
        controls_layout.addWidget(self.motif_input, 1)
        controls_layout.addWidget(self.case_sensitive)
        controls_layout.addStretch(1)
        controls_layout.addWidget(example_button)
        controls_layout.addWidget(clear_button)
        controls_layout.addWidget(find_button)
        layout.addWidget(controls)

        self.input_box, self.output_box = _add_side_by_side_editors(
            layout,
            "Input FASTA",
            "Paste FASTA records here...",
            "Motif Hits",
            "Motif match results will appear here.",
            read_only_output=True,
        )

        self.summary = QLabel("Search exact motifs and report every overlapping hit position.")
        self.summary.setWordWrap(True)
        self.summary.setObjectName("StatusLabel")
        layout.addWidget(self.summary)

    def _load_example(self) -> None:
        self.input_box.setPlainText(EXAMPLE_FASTA.strip())
        self.motif_input.setText("ATG")
        self._scan()

    def _clear_all(self) -> None:
        self.input_box.clear()
        self.motif_input.clear()
        self.output_box.clear()
        self.summary.setText("Cleared. Add FASTA content and a motif to search again.")

    def _scan(self) -> None:
        try:
            records = parse_fasta(self.input_box.toPlainText(), uppercase=True)
            matches = find_motif_matches(
                records,
                self.motif_input.text(),
                case_sensitive=self.case_sensitive.isChecked(),
            )
        except ValueError as exc:
            self.output_box.clear()
            self.summary.setText(f"Validation error: {exc}")
            return

        if not matches:
            self.output_box.setPlainText("No matches found.")
            self.summary.setText("Search completed. No motif hits were found.")
            return

        lines = ["Motif hits"]
        for match in matches:
            lines.append(
                f"- {match.header}: {match.matched_text} at {match.start}-{match.end}"
            )
        self.output_box.setPlainText("\n".join(lines))
        self.summary.setText(f"Found {len(matches)} hit(s) across {len(records)} record(s).")


class PrimerDesignerPage(QWidget):
    def __init__(self, tool: ToolSpec) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        layout.addWidget(_build_page_header(tool))

        controls = make_card()
        controls_layout = QHBoxLayout(controls)
        controls_layout.setSpacing(14)

        self.primer_length = QSpinBox()
        self.primer_length.setRange(16, 30)
        self.primer_length.setValue(20)

        self.min_gc = QDoubleSpinBox()
        self.min_gc.setRange(0.0, 100.0)
        self.min_gc.setValue(40.0)

        self.max_gc = QDoubleSpinBox()
        self.max_gc.setRange(0.0, 100.0)
        self.max_gc.setValue(60.0)

        self.top_n = QSpinBox()
        self.top_n.setRange(1, 20)
        self.top_n.setValue(5)

        example_button = QPushButton("Load Example")
        example_button.setObjectName("SecondaryButton")
        example_button.clicked.connect(self._load_example)
        clear_button = QPushButton("Clear")
        clear_button.setObjectName("SecondaryButton")
        clear_button.clicked.connect(self._clear_all)
        design_button = QPushButton("Suggest Primers")
        design_button.clicked.connect(self._design)

        controls_layout.addWidget(QLabel("Primer length"))
        controls_layout.addWidget(self.primer_length)
        controls_layout.addWidget(QLabel("Min GC"))
        controls_layout.addWidget(self.min_gc)
        controls_layout.addWidget(QLabel("Max GC"))
        controls_layout.addWidget(self.max_gc)
        controls_layout.addWidget(QLabel("Top N"))
        controls_layout.addWidget(self.top_n)
        controls_layout.addStretch(1)
        controls_layout.addWidget(example_button)
        controls_layout.addWidget(clear_button)
        controls_layout.addWidget(design_button)
        layout.addWidget(controls)

        self.input_box, self.output_box = _add_side_by_side_editors(
            layout,
            "Input FASTA",
            "Paste nucleotide FASTA records here...",
            "Primer Candidates",
            "Primer suggestions will appear here.",
            read_only_output=True,
        )

        self.summary = QLabel("This starter uses a simple heuristic scorer. Later you can swap this for Primer3.")
        self.summary.setWordWrap(True)
        self.summary.setObjectName("StatusLabel")
        layout.addWidget(self.summary)

    def _load_example(self) -> None:
        self.input_box.setPlainText(EXAMPLE_FASTA.strip())
        self._design()

    def _clear_all(self) -> None:
        self.input_box.clear()
        self.output_box.clear()
        self.summary.setText("Cleared. Paste nucleotide FASTA content to design primers again.")

    def _design(self) -> None:
        try:
            records = parse_fasta(self.input_box.toPlainText(), uppercase=True)
            result = design_primers(
                records,
                primer_length=self.primer_length.value(),
                min_gc=self.min_gc.value(),
                max_gc=self.max_gc.value(),
                top_n=self.top_n.value(),
            )
        except ValueError as exc:
            self.output_box.clear()
            self.summary.setText(f"Validation error: {exc}")
            return

        if result.scanned_records == 0:
            self.output_box.setPlainText("No nucleotide records were found to scan for primers.")
            self.summary.setText("Design completed, but no DNA or RNA records were eligible for primer scanning.")
            return

        self.output_box.setPlainText(_format_primer_result(result))
        self.summary.setText(
            f"Scanned {result.scanned_records} nucleotide record(s) and returned "
            f"{len(result.forward)} forward plus {len(result.reverse)} reverse candidates."
        )


def _build_page_header(tool: ToolSpec) -> QFrame:
    header = make_card()
    header_layout = QVBoxLayout(header)
    title_row = QHBoxLayout()
    title = QLabel(tool.name)
    title.setObjectName("HeroTitle")
    title_row.addWidget(title, 1)
    title_row.addWidget(make_badge(tool.status.title(), tool.is_ready))
    description = QLabel(tool.description)
    description.setWordWrap(True)
    description.setObjectName("HeroBody")
    header_layout.addLayout(title_row)
    header_layout.addWidget(description)
    return header


def _build_standard_actions(
    load_callback: Callable[[], None],
    clear_callback: Callable[[], None],
    action_callback: Callable[[], None],
) -> QFrame:
    controls = make_card()
    controls_layout = QHBoxLayout(controls)
    controls_layout.addStretch(1)

    example_button = QPushButton("Load Example")
    example_button.setObjectName("SecondaryButton")
    example_button.clicked.connect(load_callback)
    clear_button = QPushButton("Clear")
    clear_button.setObjectName("SecondaryButton")
    clear_button.clicked.connect(clear_callback)
    action_button = QPushButton("Run")
    action_button.clicked.connect(action_callback)

    controls_layout.addWidget(example_button)
    controls_layout.addWidget(clear_button)
    controls_layout.addWidget(action_button)
    return controls


def _add_side_by_side_editors(
    parent_layout: QVBoxLayout,
    input_title: str,
    input_placeholder: str,
    output_title: str,
    output_placeholder: str,
    read_only_output: bool = True,
) -> tuple[QPlainTextEdit, QPlainTextEdit]:
    editors = QHBoxLayout()
    editors.setSpacing(16)

    input_box = QPlainTextEdit()
    input_box.setPlaceholderText(input_placeholder)

    output_box = QPlainTextEdit()
    output_box.setReadOnly(read_only_output)
    output_box.setPlaceholderText(output_placeholder)

    input_card = make_card()
    input_layout = QVBoxLayout(input_card)
    input_heading = QLabel(input_title)
    input_heading.setObjectName("SectionTitle")
    input_layout.addWidget(input_heading)
    input_layout.addWidget(input_box)

    output_card = make_card()
    output_layout = QVBoxLayout(output_card)
    output_heading = QLabel(output_title)
    output_heading.setObjectName("SectionTitle")
    output_layout.addWidget(output_heading)
    output_layout.addWidget(output_box)

    editors.addWidget(input_card, 1)
    editors.addWidget(output_card, 1)
    parent_layout.addLayout(editors, 1)
    return input_box, output_box


def _make_stat_card(label: str, value: str) -> QFrame:
    card = QFrame()
    card.setObjectName("StatCard")
    layout = QVBoxLayout(card)
    stat_value = QLabel(value)
    stat_value.setObjectName("StatValue")
    stat_value.setAlignment(Qt.AlignCenter)
    stat_label = QLabel(label)
    stat_label.setAlignment(Qt.AlignCenter)
    layout.addWidget(stat_value)
    layout.addWidget(stat_label)
    return card


def _make_tool_launch_card(tool: ToolSpec, launch_tool: Callable[[str], None]) -> QFrame:
    card = make_card()
    layout = QVBoxLayout(card)
    header = QHBoxLayout()
    title = QLabel(tool.name)
    title.setObjectName("SectionTitle")
    header.addWidget(title, 1)
    header.addWidget(make_badge(tool.status.title(), tool.is_ready))
    description = QLabel(tool.description)
    description.setWordWrap(True)
    launch = QPushButton("Open Tool")
    launch.clicked.connect(lambda _checked=False, tool_id=tool.id: launch_tool(tool_id))
    layout.addLayout(header)
    layout.addWidget(description)
    layout.addStretch(1)
    layout.addWidget(launch)
    return card


def _format_primer_result(result: PrimerDesignResult) -> str:
    lines = ["Forward candidates"]
    lines.extend(_primer_lines(result.forward))
    lines.append("")
    lines.append("Reverse candidates")
    lines.extend(_primer_lines(result.reverse))
    return "\n".join(lines).strip()


def _primer_lines(candidates: tuple) -> list[str]:
    if not candidates:
        return ["- No candidates passed the current filters."]

    lines: list[str] = []
    for candidate in candidates:
        lines.append(
            f"- {candidate.header} | {candidate.sequence} | {candidate.start}-{candidate.end} | "
            f"GC {candidate.gc_percent:.2f}% | Tm {candidate.tm_celsius:.1f} C | score {candidate.score:.2f}"
        )
    return lines
