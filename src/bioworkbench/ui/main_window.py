from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QStackedWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from bioworkbench.core.registry import ToolRegistry
from bioworkbench.ui.pages import (
    DashboardPage,
    FastaFormatterPage,
    MotifFinderPage,
    PlaceholderToolPage,
    PrimerDesignerPage,
    SequenceSummaryPage,
    SequenceTransformPage,
)

STYLE_SHEET = """
QWidget {
    background: #efe8dc;
    color: #2c261d;
    font-family: "Segoe UI";
    font-size: 13px;
}

QFrame#Sidebar {
    background: #19383a;
    border-radius: 24px;
}

QLabel#SidebarTitle {
    color: #f7efe3;
    font-size: 24px;
    font-weight: 700;
}

QLabel#SidebarCaption {
    color: #c8d7d5;
}

QTreeWidget {
    background: transparent;
    border: none;
    color: #eff5f4;
    padding: 6px;
}

QTreeWidget::item {
    padding: 8px 10px;
    margin: 3px 0;
    border-radius: 10px;
}

QTreeWidget::item:selected {
    background: #e7b85c;
    color: #1e180f;
}

QFrame#Card, QFrame#StatCard, QGroupBox#ToolGroup {
    background: #fcfaf5;
    border: 1px solid #ddcfbf;
    border-radius: 22px;
}

QGroupBox#ToolGroup {
    margin-top: 8px;
    padding: 16px;
    font-weight: 700;
}

QGroupBox#ToolGroup::title {
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 6px;
}

QLabel#HeroTitle {
    color: #17322f;
    font-size: 28px;
    font-weight: 700;
}

QLabel#HeroBody {
    color: #54483b;
    font-size: 14px;
}

QLabel#SectionTitle {
    color: #17322f;
    font-size: 16px;
    font-weight: 700;
}

QLabel#StatusLabel {
    color: #3d3429;
    font-size: 13px;
}

QLabel#BadgeReady, QLabel#BadgePlanned {
    min-width: 90px;
    padding: 6px 12px;
    border-radius: 14px;
    font-weight: 700;
}

QLabel#BadgeReady {
    background: #d5f1d9;
    color: #1d5b28;
}

QLabel#BadgePlanned {
    background: #f2e6c8;
    color: #7b5a16;
}

QFrame#StatCard {
    min-height: 100px;
}

QLabel#StatValue {
    color: #17322f;
    font-size: 30px;
    font-weight: 700;
}

QPushButton {
    background: #17322f;
    color: #fffaf3;
    border: none;
    border-radius: 16px;
    padding: 10px 16px;
    font-weight: 700;
}

QPushButton:hover {
    background: #214641;
}

QPushButton#SecondaryButton {
    background: #e8dac6;
    color: #2c261d;
}

QPushButton#SecondaryButton:hover {
    background: #dbc9b2;
}

QPlainTextEdit, QSpinBox, QDoubleSpinBox, QLineEdit, QComboBox {
    background: #fffdfa;
    border: 1px solid #ccbda9;
    border-radius: 14px;
    padding: 10px;
}

QCheckBox {
    spacing: 6px;
}

QScrollArea {
    border: none;
}
"""


class MainWindow(QMainWindow):
    def __init__(self, registry: ToolRegistry) -> None:
        super().__init__()
        self.registry = registry
        self._pages_by_tool: dict[str, QWidget] = {}

        self.setWindowTitle("BioWorkbench Starter")
        self.resize(1400, 880)
        self.setMinimumSize(1120, 720)
        self.setStyleSheet(STYLE_SHEET)

        root = QWidget()
        layout = QHBoxLayout(root)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(18)

        layout.addWidget(self._build_sidebar(), 0)

        self.stack = QStackedWidget()
        self.dashboard_page = DashboardPage(registry, self.open_tool_by_id)
        self.stack.addWidget(self.dashboard_page)
        layout.addWidget(self.stack, 1)

        self.setCentralWidget(root)

    def _build_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(320)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(18, 22, 18, 18)
        layout.setSpacing(14)

        title = QLabel("BioWorkbench")
        title.setObjectName("SidebarTitle")
        caption = QLabel("Offline-first starter for modular genomics tools")
        caption.setObjectName("SidebarCaption")
        caption.setWordWrap(True)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.itemClicked.connect(self._handle_tree_click)

        dashboard_item = QTreeWidgetItem(["Dashboard"])
        dashboard_item.setData(0, Qt.ItemDataRole.UserRole, "__dashboard__")
        self.tree.addTopLevelItem(dashboard_item)

        for category in self.registry.categories():
            parent = QTreeWidgetItem([category])
            parent.setFlags(parent.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            for tool in self.registry.by_category(category):
                child = QTreeWidgetItem([tool.name])
                child.setData(0, Qt.ItemDataRole.UserRole, tool.id)
                parent.addChild(child)
            self.tree.addTopLevelItem(parent)

        self.tree.expandAll()
        self.tree.setCurrentItem(dashboard_item)

        footer = QLabel("Start in the dashboard, then launch a ready tool or continue building the planned workflows.")
        footer.setWordWrap(True)
        footer.setObjectName("SidebarCaption")

        layout.addWidget(title)
        layout.addWidget(caption)
        layout.addWidget(self.tree, 1)
        layout.addWidget(footer)
        return sidebar

    def _handle_tree_click(self, item: QTreeWidgetItem, _column: int) -> None:
        key = item.data(0, Qt.ItemDataRole.UserRole)
        if key == "__dashboard__":
            self.stack.setCurrentWidget(self.dashboard_page)
            return
        if not key:
            return

        self.open_tool_by_id(key)

    def open_tool_by_id(self, tool_id: str) -> None:
        if tool_id not in self._pages_by_tool:
            tool = self.registry.get(tool_id)
            page = self._build_tool_page(tool.id)
            self._pages_by_tool[tool_id] = page
            self.stack.addWidget(page)

        self.stack.setCurrentWidget(self._pages_by_tool[tool_id])

    def _build_tool_page(self, tool_id: str) -> QWidget:
        tool = self.registry.get(tool_id)
        if tool_id == "fasta_formatter":
            return FastaFormatterPage(tool)
        if tool_id == "sequence_summary":
            return SequenceSummaryPage(tool)
        if tool_id == "sequence_transform":
            return SequenceTransformPage(tool)
        if tool_id == "motif_finder":
            return MotifFinderPage(tool)
        if tool_id == "primer_designer":
            return PrimerDesignerPage(tool)
        return PlaceholderToolPage(tool)
