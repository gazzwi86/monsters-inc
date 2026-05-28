# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Purpose

Enterprise architecture reference project modeling **Monsters, Inc.** (Pixar) using the full open semantic web and EA standards stack. It is both a learning resource and a demonstration artifact for **MS IQ** — an intelligent enterprise modeling platform designed to import and reason over these open formats.

The semantic artifacts themselves (the `ontologies/`, `shapes/`, `mappings/`, and `queries/` files), together with this `CLAUDE.md` and `README.md`, are the live source of truth. The original brief is preserved for reference at `.claude/prompts/spec.md` (canonical domain knowledge, entity definitions, business rules) and `.claude/prompts/PROMPT.md` (per-artifact content requirements). That brief predates the 2026 agent-grade additions (docs 13–15, the agent/governance/constitution/motivation ontologies), so treat it as historical context — not current inventory.

---

## Commands

Once `pyproject.toml` exists (generated as part of the project build):

```bash
uv sync                  # install dependencies (rdflib, pyshacl, rich, typer)
make all                 # seed → generate ontology → validate SHACL → run queries
make ontology            # uv run mi-ontology  → merges the 9 ontologies → build/mi-merged.ttl (+ live counts)
make seed                # uv run mi-seed      → writes data/seed_graph.ttl
make validate            # uv run mi-validate  → SHACL report (expects 3 intentional violations, named)
make query               # uv run mi-query     → business questions Q1–Q22
make query-cv            # compliance · make query-agent · make query-human · make query-gov · make query-con
make test                # detector unit tests — isolated fixtures for CV5/CV6/CV3 (runs inside `make all`)
make materialize         # execute the R2RML mapping (SQLite + morph-kgc) and verify it joins the seed graph
make drift               # verify docs excerpts still match their source-of-truth files
make images              # render diagrams + query Q&A cards → images/ (PNG/SVG, gitignored)
make hooks               # install the pre-commit lint hook (ruff + black on scripts/)
make catalog             # uv run mi-catalog   → builds DCAT catalog from data assets → build/mi-catalog.generated.ttl
```

To run a single script directly:
```bash
uv run python scripts/validate_shacl.py
uv run python scripts/run_queries.py --query Q1
```

To check a Turtle file parses cleanly:
```python
import rdflib; g = rdflib.Graph(); g.parse("ontologies/mi-core.ttl", format="turtle")
```

---

## Architecture

The project has three layers that build on each other:

### 1. Documentation (`docs/`)
16 markdown files (00–15), each covering one modeling view. Every document must include: a `View / Standard / Audience` header block, a navigation bar, at least one PlantUML diagram, at least one Turtle/SPARQL/SHACL code artifact, a "Why this matters" section, and cross-references to related docs. Diagrams use **PlantUML** exclusively (not Mermaid).

### 2. Semantic Artifacts
| Path | Standard | What it models |
|------|----------|----------------|
| `ontologies/mi-core.ttl` | OWL 2 | 12 core entity classes (plus the abstract `mi:Canister` superclass and legacy `mi:ScreamCanister`), supporting enumerations, and properties — the central schema |
| `ontologies/mi-glossary.ttl` | SKOS | 52 controlled-vocabulary concepts under 7 top concepts |
| `ontologies/mi-catalog.ttl` | DCAT 3 | Catalog of all 11 data assets |
| `ontologies/mi-provenance.ttl` | PROV-O | Laugh→canister→energy→grid lineage chain |
| `ontologies/mi-process.ttl` | OWL + BPMN-O | 7 business processes with semantic annotations |
| `ontologies/mi-agent-model.ttl` | OWL 2 | Authority, permissions, HITL triggers, `mi:automatable` per step |
| `ontologies/mi-motivation.ttl` | OWL 2 | Goals/drivers/capabilities — strategy→capability→process chain |
| `ontologies/mi-governance.ttl` | OWL 2 + W3C ODRL | Identity, RDF service catalog, ODRL access policies, data classification |
| `ontologies/mi-constitution.ttl` | OWL 2 | Principles → regulatory requirements → enforcement bindings |
| `shapes/mi-core.shacl.ttl` | SHACL | Core property/cardinality constraint shapes |
| `shapes/mi-compliance.shacl.ttl` | SHACL | CDA-specific regulatory constraint shapes |
| `shapes/mi-agent.shacl.ttl` | SHACL | Permission / HITL / high-severity escalation constraint shapes |
| `mappings/mi-db.r2rml.ttl` | R2RML | Maps the operational SQL tables (COMEDIAN, CHILD_DOOR, PERFORMANCE_RECORD, …) to RDF |
| `queries/business-questions.sparql` | SPARQL 1.1 | 22 analytical business queries (Q1–Q22) |
| `queries/compliance-violations.sparql` | SPARQL 1.1 | 7 queries mirroring SHACL constraints (CV1–CV7) |
| `queries/agent-authority.sparql` | SPARQL 1.1 | 5 agent-authority queries (AA1–AA5) |
| `queries/human-centered.sparql` | SPARQL 1.1 | 8 human-centered / wellbeing queries (HC1–HC8) |
| `queries/governance.sparql` | SPARQL 1.1 | 6 data-governance queries (GV1–GV6) |
| `queries/constitution.sparql` | SPARQL 1.1 | 4 constitution / defensibility queries (CN1–CN4) |

### 3. Python / UV Project (`scripts/`)
Ten Python files in `scripts/` (`__init__.py` plus nine modules). Five are wired as CLI entry points via `pyproject.toml` (`mi-seed`, `mi-ontology`, `mi-validate`, `mi-query`, `mi-catalog`); `check_doc_drift`, `run_tests`, `materialize_r2rml`, and `render_assets` are invoked via their `make` targets. Execution order matters: `seed_data` first (populates `data/seed_graph.ttl`), then `generate_ontology`, then `validate_shacl` (loads seed + the ontologies the shapes target, including `mi-provenance.ttl`), then `run_queries` (loads all ontologies + seed into one graph). `run_tests` exercises the dormant detectors (CV5/CV6/CV3) against isolated in-memory fixtures without touching the seed; `check_doc_drift` verifies doc excerpts against their source files.

---

## Key Conventions

**Ontology URI base:** `https://vocab.monstersinc.com/ontology#`, prefix `mi:`  
**SKOS glossary URI:** `https://vocab.monstersinc.com/glossary`

**Class naming:** PascalCase OWL class names map directly to database table names (COMEDIAN → `mi:Comedian`). The 12 core classes are listed in `.claude/prompts/spec.md §6`.

**Cross-domain concern:** CDA compliance (D5) is a cross-cutting concern — it touches D1, D2, and D3. Any process or shape affecting those domains must include a CDA compliance check or reference.

**Intentional SHACL violations in seed data:** `seed_data.py` deliberately creates three violations: (1) a Comedian without valid certification (Randall Boggs), (2) a ChildDoor with stale maintenance (NYC-0099), and (3) a CDA incident reported >30 minutes after detection. `make validate` should show exactly 3 violations and name each — this is the expected state. `validate_shacl.py` asserts them by identity (not a magic count), so adding shapes won't falsely fail the check.

**Agent-grade modules (2026 council remediation):** beyond the original 12-class core, the model now includes `ontologies/mi-agent-model.ttl` (authority, permissions, HITL triggers, `mi:automatable` per step), `mi-motivation.ttl` (goals/drivers/capabilities — strategy→process chain), `mi-governance.ttl` (identity, service catalog as RDF, W3C ODRL access policies, data classification), and `mi-constitution.ttl` (principles → regulatory requirements → enforcement bindings). Query suites: `queries/{agent-authority,human-centered,governance,constitution}.sparql`. Docs `13`–`15` cover these. Docs carry short marked excerpts (not full copies) of source files — run `make drift` after editing a doc's code block.

**Diagram format:** All diagrams are PlantUML. Use `!theme plain` and `skinparam backgroundColor #FFFFFF` as baseline styling for consistency across all documents.

**Six domains (D1–D6):** D2 (Laugh Operations) is the core value-creating domain. All other domains either feed into it or regulate it. When in doubt about domain ownership of an entity, trace back to which domain it most directly enables.

---

## Execution Order for Full Generation

The initial build is complete; this dependency map is retained as reference (see `.claude/prompts/PROMPT.md` for the original per-artifact specs):

```
docs/01 → ontologies/mi-core.ttl
docs/08 → ontologies/mi-glossary.ttl
docs/02 → (no new artifact, references capability inventory from .claude/prompts/spec.md)
docs/03 → ontologies/mi-process.ttl (snippet)
docs/04 → (OBPM annotations on process from 03)
docs/10 → (entity graph, no new .ttl)
docs/11 → mappings/mi-db.r2rml.ttl
docs/09 → shapes/mi-core.shacl.ttl + shapes/mi-compliance.shacl.ttl
          queries/business-questions.sparql + queries/compliance-violations.sparql
docs/06 → ontologies/mi-provenance.ttl
docs/05 → ontologies/mi-catalog.ttl
docs/07 → (service catalog, no new .ttl)
docs/12 → (document ontology, inline Turtle only)
docs/13 → ontologies/mi-agent-model.ttl + shapes/mi-agent.shacl.ttl
          queries/agent-authority.sparql + queries/human-centered.sparql
docs/14 → ontologies/mi-governance.ttl (W3C ODRL) + queries/governance.sparql
docs/15 → ontologies/mi-constitution.ttl + queries/constitution.sparql
          (motivation chain: ontologies/mi-motivation.ttl)
scripts/ → eight modules: 5 CLI entry points (mi-seed/-ontology/-validate/-query/-catalog)
           + check_doc_drift + run_tests + materialize_r2rml + render_assets
data/    → monsters.json, doors.json, scare_records.json
README.md → navigation hub (fill last, all links known)
```
