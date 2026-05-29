"""Render blog/doc assets into ./images and embed diagram images into the docs.

GitHub does not render PlantUML (` ```plantuml ` blocks show as source code), and
most readers won't run the local PlantUML server. So this script makes the model
browsable on GitHub with zero setup by:

  1. Rendering every PlantUML diagram in docs/*.md -> images/diagrams/*.png
     (via the local PlantUML server at http://localhost:8080).
  2. Embedding a committed PNG above each ` ```plantuml ` block in the docs
     (idempotently — re-running refreshes, never duplicates), so the rendered
     diagram shows on GitHub with the PlantUML source kept underneath.
  3. Rendering a "question -> SPARQL -> answer" card per query (all six suites)
     -> images/queries/*.svg (+ 2x *.png), exported from the same Rich rendering
     `make query` produces.
  4. Writing images/README.md — a friendly index so non-technical readers can
     browse questions and diagrams at a glance.

Run: make images   (or: uv run python scripts/render_assets.py)
Needs the PlantUML server on :8080 for diagrams; `rsvg-convert` for query PNGs.

Note: a few queries have tied or partial ORDER BY, so the row order (and, for the
LIMIT-ed Q1, the exact rows) of their result tables can vary between renders. The
committed query images are therefore a representative snapshot, not a byte-stable
build output — re-running may produce equivalent images with reordered rows.
"""

import re
import shutil
import subprocess
import urllib.request
import zlib
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from run_queries import load_graph

BASE = Path(__file__).parent.parent
PLANTUML = "http://localhost:8080"
QUERY_FILES = [
    ("business-questions.sparql", "Business questions"),
    ("compliance-violations.sparql", "Compliance violations"),
    ("agent-authority.sparql", "Agent authority & automation"),
    ("human-centered.sparql", "Human-centered / wellbeing"),
    ("governance.sparql", "Data governance"),
    ("constitution.sparql", "Constitution & defensibility"),
]

_B64 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
_FENCE_RE = re.compile(r"```[A-Za-z]*\n@startuml.*?@enduml\n```", re.DOTALL)
_EMBED_RE = re.compile(r"<!-- diagram-image -->\n!\[[^\]]*\]\([^)]*\)\n\n", re.DOTALL)


def _plantuml_encode(text: str) -> str:
    data = zlib.compress(text.encode("utf-8"))[2:-4]
    out = []
    for i in range(0, len(data), 3):
        b1 = data[i]
        b2 = data[i + 1] if i + 1 < len(data) else 0
        b3 = data[i + 2] if i + 2 < len(data) else 0
        out.append(_B64[b1 >> 2])
        out.append(_B64[((b1 & 0x3) << 4) | (b2 >> 4)])
        out.append(_B64[((b2 & 0xF) << 2) | (b3 >> 6)])
        out.append(_B64[b3 & 0x3F])
    return "".join(out)


def _slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "-", text).strip("-")


def _label(block: str, fallback: str) -> str:
    m = re.search(r"^title (.+)$", block, re.MULTILINE)
    raw = m.group(1) if m else fallback
    return raw.replace("\\n", " — ").replace("]", ")").replace("|", "\\|").strip()


def render_diagrams() -> list[dict]:
    """Render each diagram; return ordered metadata per image."""
    out = BASE / "images" / "diagrams"
    out.mkdir(parents=True, exist_ok=True)
    rendered = []
    for md in sorted((BASE / "docs").glob("*.md")):
        blocks = re.findall(r"@startuml.*?@enduml", md.read_text(), re.DOTALL)
        for i, block in enumerate(blocks, 1):
            m = re.match(r"@startuml\s+(\S+)", block)
            name = _slug(m.group(1)) if m else f"diagram{i}"
            fname = f"{md.stem}__{i}__{name}.png"
            png = urllib.request.urlopen(
                f"{PLANTUML}/png/{_plantuml_encode(block)}", timeout=60
            ).read()
            (out / fname).write_bytes(png)
            rendered.append({"doc": md.stem, "fname": fname, "label": _label(block, name)})
    return rendered


def embed_in_docs(diagrams: list[dict]) -> int:
    """Insert/refresh a PNG embed above each ```plantuml block. Idempotent."""
    by_doc: dict[str, list[dict]] = {}
    for d in diagrams:
        by_doc.setdefault(d["doc"], []).append(d)
    changed = 0
    for stem, items in by_doc.items():
        path = BASE / "docs" / f"{stem}.md"
        original = path.read_text()
        text = _EMBED_RE.sub("", original)  # strip any previous auto-embeds
        fences = list(_FENCE_RE.finditer(text))
        if len(fences) != len(items):  # safety: counts must align 1:1
            console = Console()
            console.print(
                f"[yellow]skip embed {stem}: {len(fences)} fences vs {len(items)} imgs[/yellow]"
            )
            continue
        for item, fence in sorted(zip(items, fences), key=lambda z: z[1].start(), reverse=True):
            embed = f"<!-- diagram-image -->\n![{item['label']}](../images/diagrams/{item['fname']})\n\n"
            text = text[: fence.start()] + embed + text[fence.start() :]
        if text != original:
            path.write_text(text)
            changed += 1
    return changed


def parse_query_cards(path: Path):
    """Yield (qid, question_text, sparql) for each query block in a .sparql file."""
    content = path.read_text().strip()
    for block in re.split(r"\n(?=# [A-Z]{1,3}\d+:)", content):
        block = block.strip()
        if not block.startswith("# "):
            continue
        comment_lines, sparql_lines, in_query = [], [], False
        for line in block.split("\n"):
            if line.startswith(("PREFIX", "SELECT", "CONSTRUCT", "ASK", "DESCRIBE")):
                in_query = True
            if in_query:
                sparql_lines.append(line)
            elif line.startswith("#"):
                comment_lines.append(line.lstrip("# ").rstrip())
        if not sparql_lines:
            continue
        qid = comment_lines[0].split(":")[0].strip() if comment_lines else "Query"
        yield qid, "\n".join(comment_lines), "\n".join(sparql_lines)


def _result_table(graph, sparql: str):
    result_obj = graph.query(sparql)
    rows = list(result_obj)
    if result_obj.vars:
        cols = [str(v) for v in result_obj.vars]
    elif rows and hasattr(rows[0], "_fields"):
        cols = list(rows[0]._fields)
    else:
        cols = [f"var{j}" for j in range(len(rows[0]))] if rows else ["result"]
    table = Table(show_header=True, header_style="bold")
    for c in cols:
        table.add_column(c, overflow="fold")
    for row in rows:
        table.add_row(*[str(v) if v is not None else "—" for v in row])
    return table, len(rows)


def render_queries() -> list[dict]:
    """Render a Q&A card per query; return ordered metadata per card."""
    out = BASE / "images" / "queries"
    out.mkdir(parents=True, exist_ok=True)
    have_png = shutil.which("rsvg-convert") is not None
    graph = load_graph()
    cards = []
    for fname, suite_label in QUERY_FILES:
        suite = fname.replace(".sparql", "")
        for qid, question, sparql in parse_query_cards(BASE / "queries" / fname):
            console = Console(record=True, width=104)
            console.print(Panel(question, title=f"[bold]{qid}[/bold] — question", expand=True))
            try:
                console.print(Syntax(sparql, "sparql", theme="monokai", word_wrap=True))
            except Exception:  # noqa: BLE001
                console.print(Panel(sparql, title="SPARQL"))
            try:
                table, n = _result_table(graph, sparql)
                console.print(Panel.fit(table, title=f"answer — {n} row(s)"))
            except Exception as e:  # noqa: BLE001
                console.print(f"[red]Error: {e}[/red]")
            stem = f"{suite}__{qid}"
            console.save_svg(str(out / f"{stem}.svg"), title=f"Monsters, Inc. — {qid}")
            if have_png:
                subprocess.run(
                    [
                        "rsvg-convert",
                        "--zoom",
                        "2",
                        str(out / f"{stem}.svg"),
                        "-o",
                        str(out / f"{stem}.png"),
                    ],
                    check=False,
                )
            title = question.split("\n")[0]
            cards.append(
                {
                    "suite": suite,
                    "suite_label": suite_label,
                    "qid": qid,
                    "title": title,
                    "stem": stem,
                }
            )
    return cards


def write_index(diagrams: list[dict], cards: list[dict]) -> None:
    lines = [
        "# Browse the model — no setup required",
        "",
        "Pre-rendered images so you can explore on GitHub without installing or running",
        "anything. Diagrams are also embedded directly in the [docs](../docs/).",
        "",
        "## Architecture diagrams",
        "",
        "| View | Diagram |",
        "|------|---------|",
    ]
    for d in diagrams:
        lines.append(f"| {d['label']} | [{d['fname']}](diagrams/{d['fname']}) |")
    lines += [
        "",
        "## Example questions (question → SPARQL → answer)",
        "",
        "Each card shows the plain-English question, the SPARQL that answers it, and the",
        "result table — no need to run anything.",
        "",
    ]
    suites: dict[str, list[dict]] = {}
    for c in cards:
        suites.setdefault(c["suite_label"], []).append(c)
    for suite_label, items in suites.items():
        lines += [f"### {suite_label}", "", "| Question | Card |", "|----------|------|"]
        for c in items:
            title = c["title"].replace("|", "\\|")
            lines.append(f"| {title} | [{c['qid']}](queries/{c['stem']}.png) |")
        lines.append("")
    (BASE / "images" / "README.md").write_text("\n".join(lines) + "\n")


def main():
    console = Console()
    console.rule("[bold blue]Monsters, Inc. — Rendering blog/doc assets")
    diagrams = []
    try:
        diagrams = render_diagrams()
        console.print(f"[green]✓[/green] {len(diagrams)} diagrams → images/diagrams/")
        n_embed = embed_in_docs(diagrams)
        console.print(f"[green]✓[/green] embedded diagram images in {n_embed} doc(s)")
    except Exception as e:  # noqa: BLE001
        console.print(f"[red]✗ diagrams failed (is the PlantUML server on :8080?): {e}[/red]")
    cards = render_queries()
    console.print(f"[green]✓[/green] {len(cards)} query cards → images/queries/ (svg + png)")
    write_index(diagrams, cards)
    console.print("[green]✓[/green] wrote images/README.md index")


if __name__ == "__main__":
    main()
