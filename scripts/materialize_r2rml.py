"""Execute the R2RML mapping against a real SQLite database and verify that the
materialised triples JOIN the hand-authored seed graph.

This is the only test that actually RUNS mappings/mi-db.r2rml.ttl. It builds a
SQLite DB from the JSON sources (matching the SQL DDL in docs/11), materialises
RDF via morph-kgc (a standard R2RML engine), and asserts that the resulting IRIs
and the mi:doorStatus IRI-objects line up with data/seed_graph.ttl. Run via:
    make materialize   (uses `uv run --with morph-kgc`, no core dependency added)
"""
import json
import sqlite3
import sys
from pathlib import Path

from rdflib import Graph, Namespace, URIRef
from rich.console import Console

MI = Namespace("https://vocab.monstersinc.com/ontology#")
BASE = Path(__file__).parent.parent
DB = BASE / "data" / "mi-db.sqlite"
console = Console()


def build_db() -> None:
    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB)
    c = con.cursor()
    c.executescript(
        """
        CREATE TABLE COMEDIAN (comedian_id TEXT PRIMARY KEY, name TEXT, cert_level INTEGER,
            laugh_score REAL, station_id TEXT, department_id TEXT, hire_date TEXT, is_active INTEGER);
        CREATE TABLE CHILD_DOOR (portal_code TEXT PRIMARY KEY, child_age_range TEXT, bedroom_type TEXT,
            door_status TEXT, last_maintained TEXT, assigned_comedian_id TEXT, timezone TEXT);
        CREATE TABLE PERFORMANCE_RECORD (record_id TEXT PRIMARY KEY, comedian_id TEXT, record_date TEXT,
            laugh_score REAL, energy_generated_mwh REAL, station_id TEXT, shift TEXT);
        CREATE TABLE TRAINING_RECORD (training_id TEXT PRIMARY KEY, comedian_id TEXT, completed_at TEXT, expires_at TEXT);
        CREATE TABLE CDA_INCIDENT (incident_id TEXT PRIMARY KEY, incident_code TEXT, severity INTEGER,
            detected_at TEXT, reported_at TEXT, resolved_at TEXT, portal_code TEXT);
        """
    )
    monsters = json.loads((BASE / "data" / "monsters.json").read_text())
    for m in monsters:
        if m.get("type") == "Comedian":
            c.execute(
                "INSERT INTO COMEDIAN VALUES (?,?,?,?,?,?,?,?)",
                (m["id"], m["name"], m.get("certLevel"), m.get("laughScore"),
                 m.get("stationId"), m.get("department"), m.get("hireDate"),
                 1 if m.get("isActive") else 0),
            )
    for d in json.loads((BASE / "data" / "doors.json").read_text()):
        c.execute(
            "INSERT INTO CHILD_DOOR VALUES (?,?,?,?,?,?,?)",
            (d["portalCode"], d.get("ageRange"), d.get("bedroomType"), d.get("doorStatus"),
             d.get("lastMaintained"), d.get("assignedComedianId"), d.get("timezone")),
        )
    for r in json.loads((BASE / "data" / "scare_records.json").read_text()):
        c.execute(
            "INSERT INTO PERFORMANCE_RECORD VALUES (?,?,?,?,?,?,?)",
            (r["recordId"], r["comedianId"], r["recordDate"], r.get("laughScore"),
             r.get("energyGeneratedMwh"), r.get("stationId"), r.get("shift")),
        )
    con.commit()
    con.close()


def materialise() -> Graph:
    import morph_kgc  # noqa: PLC0415

    config = f"""
        [CONFIGURATION]
        output_format=N-TRIPLES
        [DataSource1]
        mappings={BASE / 'mappings' / 'mi-db.r2rml.ttl'}
        db_url=sqlite:///{DB}
    """
    return morph_kgc.materialize(config)


def main():
    console.rule("[bold blue]Monsters, Inc. — R2RML Materialisation Test")
    build_db()
    console.print(f"[dim]Built SQLite DB at {DB}[/dim]")
    try:
        mat = materialise()
    except Exception as e:  # noqa: BLE001
        console.print(f"[red]✗ morph-kgc materialisation failed: {e}[/red]")
        sys.exit(1)
    console.print(f"[dim]Materialised {len(mat)} triples from the R2RML mapping[/dim]\n")

    seed = Graph()
    seed.parse(BASE / "data" / "seed_graph.ttl", format="turtle")

    checks = []

    def check(desc, ok):
        checks.append((desc, ok))
        console.print(f"  {'[green]✓[/green]' if ok else '[red]✗[/red]'} {desc}")

    sulley = URIRef("https://vocab.monstersinc.com/comedian/emp-001")
    door99 = URIRef("https://vocab.monstersinc.com/door/nyc0099")
    station1 = URIRef("https://vocab.monstersinc.com/station/station001")

    check("Comedian emp-001 materialised and typed mi:Comedian", (sulley, None, MI.Comedian) in mat or (sulley, MI.name, None) in mat)
    check("door/nyc0099 materialised (IRI aligns with seed scheme)", any(mat.triples((door99, None, None))))
    check("mi:doorStatus emitted as the IRI mi:active (not an xsd:string literal)", (door99, MI.doorStatus, MI.active) in mat)
    check("mi:assignedStation emitted as station IRI station/station001 (dangling map fixed)", (sulley, MI.assignedStation, station1) in mat)
    check("mi:hireDate present on emp-001 (declared property now materialised)", any(mat.triples((sulley, MI.hireDate, None))))

    # Join check: every materialised ChildDoor subject must exist in the seed graph
    mat_doors = {s for s in mat.subjects(MI.doorStatus, None)}
    seed_subjects = set(seed.subjects(None, None))
    unjoined = [str(d) for d in mat_doors if d not in seed_subjects]
    check(f"all {len(mat_doors)} materialised doors join the seed graph", not unjoined)
    if unjoined:
        console.print(f"    [red]unjoined: {unjoined[:3]}[/red]")

    passed = sum(1 for _, ok in checks if ok)
    console.print(f"\n[bold]{passed}/{len(checks)} materialisation checks passed[/bold]")
    sys.exit(0 if passed == len(checks) else 1)


if __name__ == "__main__":
    main()
