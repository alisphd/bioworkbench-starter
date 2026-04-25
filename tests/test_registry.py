from bioworkbench.catalog import build_registry


def test_registry_preserves_category_order() -> None:
    registry = build_registry()
    assert registry.categories()[0] == "Utilities"
    assert registry.categories()[-1] == "Primer Design"


def test_registry_returns_ready_tools() -> None:
    registry = build_registry()
    ready_names = [tool.name for tool in registry.ready_tools()]
    assert ready_names == [
        "FASTA Formatter",
        "Sequence Summary",
        "Sequence Transform",
        "K-mer Counter",
        "Motif Finder",
        "ORF Finder",
        "GC Window Scanner",
        "Primer Designer",
    ]
