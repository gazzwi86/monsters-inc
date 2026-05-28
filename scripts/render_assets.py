"""Render blog/doc assets into ./images.

Two kinds of asset:
  - PlantUML diagrams from docs/*.md  -> images/diagrams/*.png  (via the local
    PlantUML server at http://localhost:8080)
  - SPARQL query "question + query + answer" cards -> images/queries/*.svg (+ .png)
    Each card shows the question (the query's leading comment), the SPARQL, and
    the result table, captured from a Rich console — the same rendering `make
    query` produces, exported to a publishable image.

Run: uv run python scripts/render_assets.py
Requires the PlantUML server running (for diagrams) and, for query PNGs,
`rsvg-convert` on PATH (optional — SVGs are always written).
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
    "business-questions.sparql",
    "compliance-violations.sparql",
    "agent-authority.sparql",
    "human-centered.sparql",
    "governance.sparql",
    "constitution.sparql",
]

_B64 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"


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


def render_diagrams() -> int:
    out = BASE / "images" / "diagrams"
    out.mkdir(parents=True, exist_ok=True)
    count = 0
    for md in sorted((BASE / "docs").glob("*.md")):
        blocks = re.findall(r"@startuml.*?@enduml", md.read_text(), re.DOTALL)
        for i, block in enumerate(blocks, 1):
            m = re.match(r"@startuml\s+(\S+)", block)
            name = _slug(m.group(1)) if m else f"diagram{i}"
            url = f"{PLANTUML}/png/{_plantuml_encode(block)}"
            png = urllib.request.urlopen(url, timeout=60).read()
            (out / f"{md.stem}__{i}__{name}.png").write_bytes(png)
            count += 1
    return count


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
        question = "\n".join(comment_lines)
        yield qid, question, "\n".join(sparql_lines)


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


def render_queries() -> int:
    out = BASE / "images" / "queries"
    out.mkdir(parents=True, exist_ok=True)
    have_png = shutil.which("rsvg-convert") is not None
    graph = load_graph()
    count = 0
    for fname in QUERY_FILES:
        suite = fname.replace(".sparql", "")
        path = BASE / "queries" / fname
        for qid, question, sparql in parse_query_cards(path):
            console = Console(record=True, width=104)
            console.print(Panel(question, title=f"[bold]{qid}[/bold] — question", expand=True))
            try:
                console.print(Syntax(sparql, "sparql", theme="monokai", word_wrap=True))
            except Exception:
                console.print(Panel(sparql, title="SPARQL"))
            try:
                table, n = _result_table(graph, sparql)
                console.print(Panel.fit(table, title=f"answer — {n} row(s)"))
            except Exception as e:  # noqa: BLE001
                console.print(f"[red]Error: {e}[/red]")
            stem = f"{suite}__{qid}"
            svg_path = out / f"{stem}.svg"
            console.save_svg(str(svg_path), title=f"Monsters, Inc. — {qid}")
            if have_png:
                subprocess.run(
                    ["rsvg-convert", "--zoom", "2", str(svg_path), "-o", str(out / f"{stem}.png")],
                    check=False,
                )
            count += 1
    return count


def main():
    console = Console()
    console.rule("[bold blue]Monsters, Inc. — Rendering blog assets")
    try:
        n_diag = render_diagrams()
        console.print(f"[green]✓[/green] {n_diag} diagrams → images/diagrams/")
    except Exception as e:  # noqa: BLE001
        console.print(f"[red]✗ diagrams failed (is the PlantUML server on :8080?): {e}[/red]")
    n_q = render_queries()
    console.print(f"[green]✓[/green] {n_q} query cards → images/queries/ (svg + png)")


if __name__ == "__main__":
    main()
