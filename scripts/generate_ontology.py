"""Merge the authored OWL ontologies into a single build artifact.

The nine ``ontologies/*.ttl`` files are the hand-authored source of truth. This
tool does NOT rewrite them; it loads them all, serialises the union to
``build/mi-merged.ttl`` (a single-file import for downstream consumers), and
prints a summary whose counts are derived LIVE from the merged graph — never
hardcoded.
"""

from pathlib import Path

from rdflib import Graph
from rdflib.namespace import OWL, RDF
from rich.console import Console
from rich.table import Table

BASE = Path(__file__).parent.parent
console = Console()


def main():
    console.rule("[bold blue]Monsters, Inc. — Merging OWL Ontologies")

    onto_dir = BASE / "ontologies"
    merged = Graph()

    per_file = Table(title="Ontology Sources", show_header=True, header_style="bold magenta")
    per_file.add_column("File", style="cyan")
    per_file.add_column("Triples", justify="right")
    per_file.add_column("owl:Class", justify="right")

    sources = sorted(onto_dir.glob("*.ttl"))
    for ttl in sources:
        fg = Graph()
        fg.parse(ttl, format="turtle")
        merged.parse(ttl, format="turtle")
        n_cls = len(set(fg.subjects(RDF.type, OWL.Class)))
        per_file.add_row(ttl.name, str(len(fg)), str(n_cls))

    console.print(per_file)

    # Live-derived totals over the merged graph (no hardcoded numbers).
    classes = set(merged.subjects(RDF.type, OWL.Class))
    obj_props = set(merged.subjects(RDF.type, OWL.ObjectProperty))
    dt_props = set(merged.subjects(RDF.type, OWL.DatatypeProperty))
    restrictions = set(merged.subjects(RDF.type, OWL.Restriction))
    named_inds = set(merged.subjects(RDF.type, OWL.NamedIndividual))
    disjoint_axioms = len(list(merged.triples((None, OWL.disjointWith, None)))) + len(
        set(merged.subjects(RDF.type, OWL.AllDisjointClasses))
    )

    summary = Table(
        title="Merged Ontology — Live Totals", show_header=True, header_style="bold green"
    )
    summary.add_column("Metric")
    summary.add_column("Count", justify="right")
    summary.add_row("Total triples", str(len(merged)))
    summary.add_row("owl:Class", str(len(classes)))
    summary.add_row("owl:ObjectProperty", str(len(obj_props)))
    summary.add_row("owl:DatatypeProperty", str(len(dt_props)))
    summary.add_row("owl:Restriction", str(len(restrictions)))
    summary.add_row("owl:NamedIndividual", str(len(named_inds)))
    summary.add_row("disjointness axioms", str(disjoint_axioms))
    console.print(summary)

    build_dir = BASE / "build"
    build_dir.mkdir(exist_ok=True)
    out_path = build_dir / "mi-merged.ttl"
    merged.serialize(destination=str(out_path), format="turtle")
    console.print(
        f"\n[green]✓[/green] Merged {len(sources)} ontologies "
        f"→ [bold]{out_path}[/bold] ({len(merged)} triples)\n"
    )


if __name__ == "__main__":
    main()
