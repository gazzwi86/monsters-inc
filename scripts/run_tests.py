"""Detector unit tests against isolated in-memory fixtures.

Exercises the compliance detectors that the main seed does NOT positively trigger
(CV5 filled-unsealed canister, CV6 aged-out door) plus a regression guard for the
CV3 30-minute duration fix — WITHOUT touching data/seed_graph.ttl or the
"exactly 3 intentional violations" invariant. Each query's text is loaded from the
real .sparql file (no duplicated query logic), then run against a throwaway graph.
"""
import sys
from pathlib import Path

from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, XSD
from rich.console import Console

sys.path.insert(0, str(Path(__file__).parent))
from run_queries import parse_queries  # noqa: E402

MI = Namespace("https://vocab.monstersinc.com/ontology#")
BASE = Path(__file__).parent.parent
console = Console()


def get_query(filename: str, qid: str) -> str:
    """Load a single query's text from a queries/*.sparql file by exact id."""
    for label, sparql in parse_queries(BASE / "queries" / filename):
        if label.split(":")[0].strip().upper() == qid.upper():
            return sparql
    raise SystemExit(f"query {qid} not found in {filename}")


def rowcount(graph: Graph, sparql: str) -> int:
    return len(list(graph.query(sparql)))


def door(g: Graph, uri: str, code: str, age_range: str) -> None:
    d, p = URIRef(uri), URIRef(uri + "-profile")
    g.add((d, RDF.type, MI.ChildDoor))
    g.add((d, MI.portalCode, Literal(code)))
    g.add((d, MI.childProfile, p))
    g.add((p, MI.ageRange, Literal(age_range)))


def canister(g: Graph, uri: str, fill: float, sealed: bool) -> None:
    c = URIRef(uri)
    g.add((c, RDF.type, MI.LaughCanister))
    g.add((c, MI.fillLevel, Literal(fill, datatype=XSD.decimal)))
    g.add((c, MI.sealStatus, Literal(sealed)))


def incident(g: Graph, uri: str, detected: str, reported: str) -> None:
    i = URIRef(uri)
    g.add((i, RDF.type, MI.CDAIncident))
    g.add((i, MI.incidentCode, Literal("2319")))
    g.add((i, MI.detectedAt, Literal(detected, datatype=XSD.dateTime)))
    g.add((i, MI.reportedAt, Literal(reported, datatype=XSD.dateTime)))


TESTS = []


def test(name):
    def deco(fn):
        TESTS.append((name, fn))
        return fn
    return deco


@test("CV6 flags an aged-out (14-16) door")
def _(cv6):
    g = Graph(); door(g, "urn:d1", "AGE-14", "14-16")
    assert rowcount(g, cv6) == 1


@test("CV6 ignores an in-range (5-7) door")
def _(cv6):
    g = Graph(); door(g, "urn:d2", "AGE-7", "5-7")
    assert rowcount(g, cv6) == 0


@test("CV6 handles the '13+' format (strips the '+')")
def _(cv6):
    g = Graph(); door(g, "urn:d3", "AGE-13plus", "13+")
    assert rowcount(g, cv6) == 1


@test("CV6 boundary: '12-14' is in-range (lower age 12 < 13)")
def _(cv6):
    g = Graph(); door(g, "urn:d4", "AGE-12", "12-14")
    assert rowcount(g, cv6) == 0


@test("CV5 flags a filled but unsealed canister")
def _(cv5):
    g = Graph(); canister(g, "urn:c1", 0.8, False)
    assert rowcount(g, cv5) == 1


@test("CV5 ignores a sealed canister")
def _(cv5):
    g = Graph(); canister(g, "urn:c2", 0.8, True)
    assert rowcount(g, cv5) == 0


@test("CV3 flags a 75-min-late incident, passes a 20-min one")
def _(cv3):
    g = Graph()
    incident(g, "urn:late", "2026-01-01T10:00:00Z", "2026-01-01T11:15:00Z")
    incident(g, "urn:ok", "2026-01-01T10:00:00Z", "2026-01-01T10:20:00Z")
    assert rowcount(g, cv3) == 1


def main():
    cache = {qid: get_query("compliance-violations.sparql", qid) for qid in ("CV3", "CV5", "CV6")}
    console.rule("[bold blue]Monsters, Inc. — Detector Tests")
    passed = failed = 0
    for name, fn in TESTS:
        arg = name.split()[0].lower()  # e.g. "cv6"
        try:
            fn(cache[arg.upper()])
            console.print(f"[green]✓ PASS[/green] {name}")
            passed += 1
        except AssertionError as e:
            console.print(f"[red]✗ FAIL[/red] {name}  ({e})")
            failed += 1
        except Exception as e:  # noqa: BLE001
            console.print(f"[red]✗ ERROR[/red] {name}: {e}")
            failed += 1
    console.print(f"\n[bold]{passed} passed, {failed} failed[/bold]")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
