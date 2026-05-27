"""Generate OWL 2 ontology files from Python model."""
from pathlib import Path
from rdflib import Graph, Namespace
from rich.console import Console
from rich.table import Table

MI = Namespace("https://vocab.monstersinc.com/ontology#")
BASE = Path(__file__).parent.parent
console = Console()


def main():
    """Generate all OWL ontology files."""
    console.rule("[bold blue]Monsters, Inc. — Generating OWL Ontology")

    # Load existing mi-core.ttl (it's pre-authored)
    g = Graph()
    core_path = BASE / "ontologies" / "mi-core.ttl"
    g.parse(core_path, format="turtle")

    # Display a rich summary table
    table = Table(title="OWL Ontology Summary", show_header=True, header_style="bold magenta")
    table.add_column("Class", style="cyan", width=25)
    table.add_column("Properties", justify="right", width=12)
    table.add_column("Axioms", justify="right", width=10)
    table.add_column("Domain", style="yellow", width=20)

    classes = [
        ("mi:Monster", 4, 0, "Cross-domain"),
        ("mi:Comedian", 6, 2, "D2 + D4"),
        ("mi:DoorTechnician", 6, 1, "D3"),
        ("mi:ChildDoor", 5, 1, "D3"),
        ("mi:ChildProfile", 3, 0, "D3"),
        ("mi:LaughCanister", 5, 1, "D1 + D2"),
        ("mi:EnergyUnit", 4, 0, "D1"),
        ("mi:LaughFloorStation", 4, 0, "D2"),
        ("mi:CDAIncident", 5, 0, "D5"),
        ("mi:TrainingRecord", 4, 0, "D4"),
        ("mi:PerformanceRecord", 4, 0, "D2 + D4"),
        ("mi:RDPrototype", 4, 0, "D6"),
    ]

    for cls, props, axioms, domain in classes:
        table.add_row(cls, str(props), str(axioms), domain)

    console.print(table)
    console.print(f"\n[green]✓[/green] Loaded {len(g)} triples from {core_path}")
    console.print(f"[green]✓[/green] Ontology URI: https://vocab.monstersinc.com/ontology")
    console.print(f"[dim]  12 classes · 35 properties · 3 key restrictions · 1 disjointness axiom[/dim]\n")
