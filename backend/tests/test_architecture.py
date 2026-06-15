"""
Architecture gate tests (test strategy §5.2).

- test_matcher_stdlib_only: walks app/matcher/ with ast and asserts every
  import root is the standard library or app.matcher itself (NFR-9).
- test_harness_running: trivial smoke confirming pytest and the app package
  are reachable.

These tests run vacuously on the empty skeleton and bite the moment a later
ticket introduces an illegal import or uncovered matcher code.
"""
import ast
import sys
from pathlib import Path

MATCHER_ROOT = Path(__file__).parent.parent / "app" / "matcher"


def _collect_imports(path: Path) -> list[tuple[str, str]]:
    """Return (root_package, full_module_name) for every absolute import in path."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    results: list[tuple[str, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                results.append((root, alias.name))
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:  # absolute import only
                root = node.module.split(".")[0]
                results.append((root, node.module))
    return results


def test_matcher_stdlib_only() -> None:
    """NFR-9: app/matcher/ must import only the standard library or app.matcher."""
    stdlib = sys.stdlib_module_names  # available since Python 3.10

    violations: list[str] = []
    for path in sorted(MATCHER_ROOT.rglob("*.py")):
        for root, full in _collect_imports(path):
            if root in stdlib:
                continue
            if full == "app.matcher" or full.startswith("app.matcher."):
                continue
            rel = path.relative_to(MATCHER_ROOT.parent.parent)
            violations.append(f"  {rel}: imports '{full}'")

    assert not violations, (
        "NFR-9 violation — app/matcher/ must import standard library only "
        "(test strategy §5.2). Offending imports:\n" + "\n".join(violations)
    )


def test_harness_running() -> None:
    """Confirm pytest is reachable and the app package is importable."""
    from app.main import create_app

    assert create_app() is not None
