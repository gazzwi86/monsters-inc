#!/usr/bin/env python3
"""Doc/Source drift checker for the Monsters, Inc. EA reference project.

The source artifacts (`.ttl`, `.sparql`, `.sql`) are the single source of truth.
Several Markdown docs in `docs/` show SHORT excerpts of those files, each marked
with an HTML comment of the form:

    <!-- excerpt-from: ontologies/mi-core.ttl -->
    ```turtle
    ...verbatim excerpt lines...
    ```

This script walks every `docs/*.md`, finds each such marker, reads the fenced
code block that immediately follows it, and verifies that every non-blank,
non-comment line of the excerpt still appears (as a stripped substring) in the
named source file. Any excerpt line not found in its source is reported as
drift. Exit code 1 if any drift is found, 0 if clean.

Pure standard library; uses `rich` for output if available, plain print otherwise.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Repo root is the parent of the directory holding this script.
REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"

MARKER = "<!-- excerpt-from:"
FENCE = "```"
# Comment prefixes to skip when checking excerpt lines (Turtle / SPARQL / SQL).
COMMENT_PREFIXES = ("#", "--")


def _print_plain(msg: str) -> None:
    print(msg)


try:  # optional pretty output
    from rich.console import Console  # type: ignore

    _console = Console()

    def out(msg: str) -> None:
        _console.print(msg)

except Exception:  # pragma: no cover - rich not installed

    def out(msg: str) -> None:
        # Strip simple rich markup so plain output stays readable.
        for tag in (
            "[red]",
            "[/red]",
            "[green]",
            "[/green]",
            "[yellow]",
            "[/yellow]",
            "[bold]",
            "[/bold]",
            "[dim]",
            "[/dim]",
        ):
            msg = msg.replace(tag, "")
        _print_plain(msg)


def parse_excerpts(md_path: Path):
    """Yield (source_rel_path, [excerpt_lines]) for each marker in a doc."""
    lines = md_path.read_text(encoding="utf-8").splitlines()
    i = 0
    n = len(lines)
    while i < n:
        stripped = lines[i].strip()
        if stripped.startswith(MARKER):
            # Extract the source path between the marker prefix and '-->'.
            inner = stripped[len(MARKER) :]
            inner = inner.replace("-->", "").strip()
            source_rel = inner
            # Find the opening fence on a following line.
            j = i + 1
            while j < n and not lines[j].lstrip().startswith(FENCE):
                # Allow only blank lines between marker and fence.
                if lines[j].strip():
                    break
                j += 1
            if j < n and lines[j].lstrip().startswith(FENCE):
                # Collect lines until the closing fence.
                block = []
                k = j + 1
                while k < n and not lines[k].lstrip().startswith(FENCE):
                    block.append(lines[k])
                    k += 1
                yield source_rel, block, j + 1  # 1-based first content line no.
                i = k + 1
                continue
        i += 1


def check_excerpt(
    source_rel: str,
    block,
):
    """Return list of (line_no_within_block, line_text) that are NOT in source."""
    source_path = REPO_ROOT / source_rel
    if not source_path.exists():
        return None  # signals missing source
    source_text = source_path.read_text(encoding="utf-8")
    misses = []
    for idx, raw in enumerate(block):
        line = raw.strip()
        if not line:
            continue
        if any(line.startswith(p) for p in COMMENT_PREFIXES):
            continue
        if line not in source_text:
            misses.append((idx, raw))
    return misses


def main() -> int:
    if not DOCS_DIR.is_dir():
        out(f"[red]docs/ directory not found at {DOCS_DIR}[/red]")
        return 1

    total_excerpts = 0
    drifted_excerpts = 0
    drift_records = []

    for md_path in sorted(DOCS_DIR.glob("*.md")):
        for source_rel, block, content_start in parse_excerpts(md_path):
            total_excerpts += 1
            result = check_excerpt(source_rel, block)
            rel_doc = md_path.relative_to(REPO_ROOT)
            if result is None:
                drifted_excerpts += 1
                drift_records.append(
                    f"[red]MISSING SOURCE[/red] {rel_doc} -> {source_rel} (file not found)"
                )
                continue
            if result:
                drifted_excerpts += 1
                drift_records.append(f"[red]DRIFT[/red] {rel_doc} (excerpt-from: {source_rel})")
                for idx, raw in result:
                    line_no = content_start + idx
                    drift_records.append(
                        f"    line {line_no}: not found in source -> {raw.strip()}"
                    )

    out("")
    out("[bold]Doc/Source Drift Check[/bold]")
    out("-" * 42)
    if drift_records:
        for rec in drift_records:
            out(rec)
        out("-" * 42)

    clean = total_excerpts - drifted_excerpts
    if drifted_excerpts == 0:
        out(f"[green]{total_excerpts} excerpts checked, 0 drifted — all in sync.[/green]")
        return 0
    out(
        f"[red]{total_excerpts} excerpts checked, {drifted_excerpts} drifted "
        f"({clean} clean).[/red]"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
