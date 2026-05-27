"""Build a DCAT catalog of the project's data assets from what's on disk.

The hand-authored ``ontologies/mi-catalog.ttl`` remains the source of truth. This
tool derives a DCAT catalog from the ACTUAL data assets (record counts read live
from the files), serialises it to ``build/mi-catalog.generated.ttl``, and
cross-checks the generated dataset count against the authored catalog so drift
between the data on disk and the authored catalog is visible.
"""

import json
from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS
from rich.console import Console
from rich.table import Table

console = Console()
BASE = Path(__file__).parent.parent

DCAT = Namespace("http://www.w3.org/ns/dcat#")
DCT = Namespace("http://purl.org/dc/terms/")
MI = Namespace("https://vocab.monstersinc.com/ontology#")
GEN = Namespace("https://vocab.monstersinc.com/catalog/generated#")

# title + format per known data asset; record counts are read live (never hardcoded).
DATA_ASSETS = {
    "monsters.json": ("Monster Employee Registry", "JSON"),
    "doors.json": ("Door Inventory (seed)", "JSON"),
    "scare_records.json": ("Performance Records (seed)", "JSON"),
    "seed_graph.ttl": ("Seed Knowledge Graph", "Turtle"),
}


def record_count(path: Path) -> str:
    """Return a live record/triple count display for a data asset."""
    if not path.exists():
        return "pending"
    if path.suffix == ".json":
        try:
            return str(len(json.loads(path.read_text())))
        except Exception:
            return "?"
    if path.suffix == ".ttl":
        try:
            g = Graph()
            g.parse(path, format="turtle")
            return f"{len(g)} triples"
        except Exception:
            return "?"
    return "—"


def main():
    console.rule("[bold blue]Monsters, Inc. — Building DCAT Catalog")
    data_dir = BASE / "data"

    cat = Graph()
    cat.bind("dcat", DCAT)
    cat.bind("dct", DCT)
    catalog_uri = GEN["catalog"]
    cat.add((catalog_uri, RDF.type, DCAT.Catalog))
    cat.add((catalog_uri, DCT.title, Literal("Monsters, Inc. — Generated Data Asset Catalog")))

    table = Table(
        title="Data Asset Inventory (live)", show_header=True, header_style="bold magenta"
    )
    table.add_column("File", style="cyan")
    table.add_column("Title")
    table.add_column("Format")
    table.add_column("Records", justify="right")
    table.add_column("Status")

    generated_datasets = 0
    for filename, (title, fmt) in DATA_ASSETS.items():
        path = data_dir / filename
        display = record_count(path)
        exists = path.exists()
        if exists:
            slug = filename.replace(".", "_")
            ds = GEN[slug]
            cat.add((ds, RDF.type, DCAT.Dataset))
            cat.add((ds, DCT.title, Literal(title)))
            cat.add((ds, DCT["format"], Literal(fmt)))
            dist = GEN[slug + "_dist"]
            cat.add((dist, RDF.type, DCAT.Distribution))
            cat.add((dist, DCAT.downloadURL, URIRef((data_dir / filename).as_uri())))
            cat.add((ds, DCAT.distribution, dist))
            cat.add((catalog_uri, DCAT.dataset, ds))
            cat.add((ds, RDFS.label, Literal(f"{title} ({display})")))
            generated_datasets += 1
        status = "[green]✓[/green]" if exists else "[dim]pending[/dim]"
        table.add_row(filename, title, fmt, display, status)

    console.print(table)

    build_dir = BASE / "build"
    build_dir.mkdir(exist_ok=True)
    out_path = build_dir / "mi-catalog.generated.ttl"
    cat.serialize(destination=str(out_path), format="turtle")
    console.print(
        f"\n[green]✓[/green] Generated DCAT catalog ({generated_datasets} datasets) "
        f"→ [bold]{out_path}[/bold]"
    )

    # Cross-check against the authored catalog so on-disk/authored drift is visible.
    authored_path = BASE / "ontologies" / "mi-catalog.ttl"
    if authored_path.exists():
        authored = Graph()
        authored.parse(authored_path, format="turtle")
        authored_assets = len(set(authored.objects(None, DCAT.dataset)))
        console.print(
            f"[dim]Authored mi-catalog.ttl catalogs {authored_assets} data asset(s); "
            f"generated catalog covers {generated_datasets} on-disk data file(s).[/dim]\n"
        )


if __name__ == "__main__":
    main()
