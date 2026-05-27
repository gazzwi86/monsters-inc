"""Build DCAT catalog from data inventory."""
import json
from pathlib import Path
from rdflib import Graph, Namespace
from rich.console import Console
from rich.table import Table

console = Console()
BASE = Path(__file__).parent.parent

DCAT = Namespace("http://www.w3.org/ns/dcat#")
DCT = Namespace("http://purl.org/dc/terms/")
MI = Namespace("https://vocab.monstersinc.com/ontology#")


def main():
    console.rule("[bold blue]Monsters, Inc. — Building DCAT Catalog")

    catalog_path = BASE / "ontologies" / "mi-catalog.ttl"
    g = Graph()
    if catalog_path.exists():
        g.parse(catalog_path, format="turtle")

    # Inventory data assets in data/ directory
    data_dir = BASE / "data"

    data_files = {
        "monsters.json": {
            "title": "Monster Employee Registry",
            "description": "25 monster employee instances including Sulley, Mike, and key staff.",
            "domain": "HRTraining",
            "format": "JSON",
            "update": "Real-time",
        },
        "doors.json": {
            "title": "Door Inventory (seed)",
            "description": "50 child-room portal door records with status and maintenance dates.",
            "domain": "DoorManagement",
            "format": "JSON",
            "update": "Daily",
        },
        "scare_records.json": {
            "title": "Performance Records (seed)",
            "description": "100 comedian performance records spanning 2021–2024.",
            "domain": "LaughOperations",
            "format": "JSON",
            "update": "Daily",
        },
        "seed_graph.ttl": {
            "title": "Seed Knowledge Graph",
            "description": "RDF graph with all seed instances for validation and query testing.",
            "domain": "LaughOperations",
            "format": "Turtle",
            "update": "On-generate",
        },
    }

    table = Table(title="Data Asset Inventory", show_header=True, header_style="bold magenta")
    table.add_column("File", style="cyan", width=25)
    table.add_column("Title", width=35)
    table.add_column("Format", width=8)
    table.add_column("Domain", width=18)
    table.add_column("Records", justify="right", width=8)
    table.add_column("Status", width=8)

    for filename, meta in data_files.items():
        filepath = data_dir / filename
        exists = filepath.exists()
        records = "—"
        if exists and filename.endswith(".json"):
            try:
                data = json.loads(filepath.read_text())
                records = str(len(data))
            except Exception:
                records = "?"
        elif exists and filename.endswith(".ttl"):
            try:
                tg = Graph()
                tg.parse(filepath, format="turtle")
                records = f"{len(tg)}T"
            except Exception:
                records = "?"

        status = "[green]✓[/green]" if exists else "[dim]pending[/dim]"
        table.add_row(filename, meta["title"], meta["format"], meta["domain"], records, status)

    console.print(table)
    console.print(f"\n[green]✓[/green] Catalog loaded: {len(g)} triples in mi-catalog.ttl")
    console.print(f"[dim]Run 'make seed' to generate seed_graph.ttl if missing[/dim]\n")
