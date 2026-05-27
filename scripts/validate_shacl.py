"""Validate seed data against SHACL shapes."""

import sys
from pathlib import Path

from pyshacl import validate
from rdflib import Graph, Namespace
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
BASE = Path(__file__).parent.parent

SH_NS = Namespace("http://www.w3.org/ns/shacl#")


def main():
    console.rule("[bold blue]Monsters, Inc. — SHACL Validation")

    # Load data graph: seed + the ontologies the shapes target. mi-process and
    # mi-agent-model are included so the agent-model shapes (Permission, HITL,
    # high-severity escalation) validate against real data — not orphaned.
    data_graph = Graph()
    seed_path = BASE / "data" / "seed_graph.ttl"

    if not seed_path.exists():
        console.print("[red]✗[/red] seed_graph.ttl not found — run [bold]make seed[/bold] first")
        sys.exit(1)

    data_graph.parse(seed_path, format="turtle")
    for onto in (
        "mi-core.ttl",
        "mi-process.ttl",
        "mi-agent-model.ttl",
        "mi-motivation.ttl",
        "mi-governance.ttl",
        "mi-constitution.ttl",
        # mi-provenance carries the only LaughCanister / EnergyUnit instances, so it
        # must load for the canister shapes to validate real nodes (not pass empty).
        "mi-provenance.ttl",
    ):
        data_graph.parse(BASE / "ontologies" / onto, format="turtle")

    # Load SHACL shapes
    shapes_graph = Graph()
    for shapes_file in (BASE / "shapes").glob("*.ttl"):
        shapes_graph.parse(shapes_file, format="turtle")

    console.print(f"[dim]Data graph: {len(data_graph)} triples[/dim]")
    console.print(f"[dim]Shapes graph: {len(shapes_graph)} triples[/dim]\n")

    # Run validation
    conforms, results_graph, results_text = validate(
        data_graph,
        shacl_graph=shapes_graph,
        inference="rdfs",
        abort_on_first=False,
        allow_infos=True,
        allow_warnings=True,
    )

    if conforms:
        console.print(
            Panel("[green]✓ Data conforms to all SHACL shapes[/green]", title="Validation Result")
        )
    else:
        table = Table(title="SHACL Validation Results", show_header=True, header_style="bold red")
        table.add_column("#", width=3, justify="right")
        table.add_column("Severity", width=10)
        table.add_column("Focus Node", width=40, style="cyan")
        table.add_column("Message", style="yellow")

        violation_count = 0
        warning_count = 0
        row_num = 0
        violation_focuses: list[str] = []

        for result in results_graph.subjects(SH_NS.resultSeverity, None):
            severity_uri = results_graph.value(result, SH_NS.resultSeverity)
            focus = results_graph.value(result, SH_NS.focusNode)
            message = results_graph.value(result, SH_NS.resultMessage)

            focus_full = str(focus) if focus else "unknown"
            msg_str = str(message) if message else "(no message)"

            if severity_uri and str(severity_uri).endswith("Violation"):
                sev_str = "[red]Violation[/red]"
                violation_count += 1
                violation_focuses.append(f"{focus_full} || {msg_str}")
            else:
                sev_str = "[yellow]Warning[/yellow]"
                warning_count += 1

            row_num += 1
            focus_str = focus_full.rstrip("/").split("/")[-1].split("#")[-1] if focus else "unknown"

            table.add_row(str(row_num), sev_str, focus_str, msg_str)

        console.print(table)
        console.print(
            f"\n[bold]Summary:[/bold] {violation_count} violation(s), {warning_count} warning(s)"
        )

        # Assert the intentional violations by identity (not by a brittle magic
        # count) so adding new shapes later does not falsely fail this check.
        # Identify the intentional violations by focus-node identity (not by
        # free-text message wording, which could be reworded).
        expected = {
            "Randall Boggs — cert expired (ComedianCertShape)": lambda blobs: any(
                "emp-009" in b.lower() for b in blobs
            ),
            "Door NYC-0099 — maintenance >180 days (DoorDispatchShape)": lambda blobs: any(
                "nyc0099" in b.lower() for b in blobs
            ),
            "Late CDA incident — reported >30 min after detection (CDAReportingShape)": lambda blobs: any(
                "/incident/" in b for b in blobs
            ),
        }
        present = {label: check(violation_focuses) for label, check in expected.items()}
        for label, ok in present.items():
            mark = "[green]✓[/green]" if ok else "[red]✗ MISSING[/red]"
            console.print(f"  {mark} {label}")
        if all(present.values()) and violation_count == len(expected):
            console.print(
                "[green]✓ Exactly the 3 intentional violations present — no unexpected violations.[/green]"
            )
        elif not all(present.values()):
            console.print(
                "[red]⚠ One or more expected intentional violations were NOT detected — check seed/shapes.[/red]"
            )
        else:
            console.print(
                f"[red]⚠ {violation_count} violations found but only 3 are intentional — "
                f"there are unexpected violations to investigate.[/red]"
            )
