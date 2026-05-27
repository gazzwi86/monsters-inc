"""Execute SPARQL business queries against the knowledge graph."""
import typer
import re
from pathlib import Path
from typing import Optional
from rdflib import ConjunctiveGraph
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

app = typer.Typer()
console = Console()
BASE = Path(__file__).parent.parent


def load_graph() -> ConjunctiveGraph:
    g = ConjunctiveGraph()
    for ttl in (BASE / "ontologies").glob("*.ttl"):
        g.parse(ttl, format="turtle")
    seed = BASE / "data" / "seed_graph.ttl"
    if seed.exists():
        g.parse(seed, format="turtle")
    return g


def parse_queries(sparql_file: Path) -> list[tuple[str, str]]:
    """Parse individual queries from a multi-query SPARQL file. Returns (label, query) pairs."""
    content = sparql_file.read_text()
    queries = []
    # Split on lines starting with a query id header, e.g. "# Q1:", "# CV3:",
    # "# HC2:", "# AA1:" — any 1–3 uppercase letters followed by a number.
    blocks = re.split(r"\n(?=# [A-Z]{1,3}\d+:)", content.strip())
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = block.split("\n")
        label = lines[0].lstrip("# ").strip() if lines[0].startswith("#") else "Query"
        # Find the actual SPARQL (starts at PREFIX or SELECT)
        sparql_lines = []
        in_query = False
        for line in lines:
            if line.startswith(("PREFIX", "SELECT", "CONSTRUCT", "ASK", "DESCRIBE")):
                in_query = True
            if in_query:
                sparql_lines.append(line)
        if sparql_lines:
            queries.append((label, "\n".join(sparql_lines)))
    return queries


@app.command()
def run(
    query: Optional[str] = typer.Option(None, "--query", "-q", help="Run a single query by ID (e.g. Q1, CV3, HC2, AA1)"),
    file: str = typer.Option("business-questions.sparql", "--file", "-f", help="SPARQL file in queries/ to run"),
):
    """Run SPARQL queries from a queries/*.sparql file against the Monsters Inc. knowledge graph."""
    console.rule(f"[bold blue]Monsters, Inc. — SPARQL Queries ({file})")

    g = load_graph()
    console.print(f"[dim]Knowledge graph loaded: {len(g)} triples[/dim]\n")

    queries_file = BASE / "queries" / file
    if not queries_file.exists():
        console.print(f"[red]✗[/red] {file} not found in queries/")
        raise typer.Exit(1)

    all_queries = parse_queries(queries_file)

    # Filter to single query if --query specified
    if query:
        q_id = query.upper()
        all_queries = [(label, sparql) for label, sparql in all_queries if q_id in label]
        if not all_queries:
            console.print(f"[red]Query {query} not found[/red]")
            raise typer.Exit(1)

    for i, (label, sparql) in enumerate(all_queries, 1):
        console.print(Panel(f"[bold cyan]{label}[/bold cyan]", expand=False))
        try:
            result_obj = g.query(sparql)
            results = list(result_obj)
            if not results:
                console.print("[dim]  (no results)[/dim]\n")
                continue

            # Build rich table from results
            if result_obj.vars:
                vars_ = [str(v) for v in result_obj.vars]
            elif hasattr(results[0], "_fields"):
                vars_ = list(results[0]._fields)
            else:
                vars_ = [f"var{j}" for j in range(len(results[0]))]

            table = Table(show_header=True, header_style="bold")
            for var in vars_:
                table.add_column(var, overflow="fold")

            for row in results:
                table.add_row(*[str(v) if v is not None else "[dim]—[/dim]" for v in row])

            console.print(table)
            console.print(f"[dim]  {len(results)} row(s)[/dim]\n")
        except Exception as e:
            console.print(f"[red]Error executing query: {e}[/red]\n")

    console.print(f"[green]✓ Executed {len(all_queries)} quer{'y' if len(all_queries) == 1 else 'ies'}[/green]")


def main():
    app()
