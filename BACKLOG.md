# Backlog — Deferred & Optional Work

Status as of the 2026-05-27 council remediation. The core model is complete and
verified: `make all` is green (exactly 3 intentional SHACL violations, all six
query suites + detector tests pass), `make materialize` passes 6/6, `make drift`
is clean. The items below were **deliberately deferred or left optional** — none
is a half-finished change. Each is written to be actioned independently.

History: `.claude/plans/council-review-2026-05-27-round2.md` (the executed plan)
and the three commits on `main` (`git log`).

---

## 1. C4 model diagrams for the service catalog  ·  Priority: Low

**What:** Add C4 (Context / Container / Component) diagrams for the application &
technology services, complementing the existing ArchiMate-style PlantUML.

**Why:** You flagged this as a low-priority fidelity enhancement. The services are
now real RDF individuals (see item context below), so the diagrams can be derived
from data rather than hand-drawn.

**Where / how:**
- Source of truth for services: `ontologies/mi-governance.ttl` — `mi:ApplicationService`
  / `mi:TechnologyService` individuals (LFMS, DPCS, ELS, HRCP, CDACG, RDLMS + 6 tech
  services), with `mi:dependsOn`, `mi:servesDomain`, `mi:accessesDataset`.
- Add a new section to `docs/07-service-catalog.md` (or a new `docs/16-c4-views.md`)
  with 3 PlantUML diagrams: System Context (Monsters Inc + CDA + Grid + Monsters U),
  Container (the 12 services + RDF store + event bus), Component (decompose LFMS).
- Use `!theme plain` + `skinparam backgroundColor #FFFFFF`. PlantUML supports the
  C4 stdlib via `!include <C4/C4_Container>` if the local server has it; otherwise
  model the boxes manually.
- Optionally generate dependency edges from a SPARQL query over `mi:dependsOn`
  (GV5 already returns the dependency map).

**Verify:** render via the local PlantUML server (`localhost:8080/png/~h<hex>`); add
nav links; run `make drift` if you add any source excerpts.

---

## 2. `mi:EnergyLedger` URI collision (SKOS concept vs DCAT dataset)  ·  Priority: Medium

**What:** The IRI `mi:EnergyLedger` is used for **two different things**: a
`skos:Concept` (a narrower term of `mi:LaughEnergy`) in `ontologies/mi-glossary.ttl`
(~line 204), AND a `dcat:Dataset` in `ontologies/mi-catalog.ttl` (~line 79) that
also carries `mi:dataClassification` + `mi:governedByPolicy` in
`ontologies/mi-governance.ttl`.

**Why it matters:** When the graphs are merged, a DCAT dataset appears as a
"narrower term of Laugh Energy", and a glossary concept appears as an
access-controlled asset. A dataset is not a kind of energy — this is semantically
wrong (unlike the *documented* dual-use OWL-class/SKOS-concept pattern for
`mi:CDAIncident`/`mi:Comedian`/`mi:ChildProfile`, see comment at
`mi-glossary.ttl` ~line 488).

**How to fix (pick one):**
- **Rename the glossary concept** to a distinct IRI, e.g. `mi:EnergyLedgerConcept`,
  and update its `skos:broader`/the parent's `skos:narrower` (the `mi:LaughEnergy`
  block lists `mi:EnergyLedger` as `skos:narrower` ~line 49). Leave the DCAT
  dataset IRI unchanged. This is the lower-blast-radius option (the dataset IRI is
  referenced from catalog + governance + the `make catalog` script).
- Or rename the dataset (higher blast radius: `mi-catalog.ttl`, `mi-governance.ttl`
  classification/policy triples, README/docs references).

**Verify:** `make ontology`/`make all` still green; `make drift`; grep that no
dangling reference to the old IRI remains: `grep -rn "EnergyLedger" ontologies docs scripts`.

---

## 3. Undocumented class+concept punning (`DoorStatus`, `TrainingProgram`)  ·  Priority: Low

**What:** `mi:DoorStatus` is an `owl:Class` (enumeration, `mi-core.ttl` ~line 23)
AND a `skos:Concept` (`mi-glossary.ttl` ~line 345). Same for `mi:TrainingProgram`
(`mi-core.ttl` ~line 78 / `mi-glossary.ttl` ~line 452). These puns are NOT covered
by the documented dual-use note (which only sanctions CDAIncident/Comedian/ChildProfile).

**Why it matters:** Under OWL DL this is punning that a strict reasoner flags; an
agent treating the glossary as the authoritative concept set sees an enumeration
class as a vocabulary term with no documented contract.

**How to fix (pick one):**
- Extend the dual-use comment in `mi-glossary.ttl` (~line 488) to explicitly list
  `DoorStatus` and `TrainingProgram` as sanctioned puns, and add `skos:exactMatch`
  alignments between the concept and the class — cheapest, documents intent.
- Or give the SKOS concepts distinct IRIs (`mi:DoorStatusConcept`, etc.).

**Verify:** `make all` green; `make drift`.

---

## 4. GV6 governance gaps — restricted datasets without an ODRL policy  ·  Priority: Medium

**What:** `make query-gov` → **GV6** currently returns 3 rows: `CDAIncidentLog`,
`CDAComplianceReports`, `RDPrototypes` are classified `Restricted` but have no
`mi:governedByPolicy` ODRL policy. (GV6 exists *to find* these — it is an honest
self-audit, not a bug.)

**Why it matters:** To present full governance coverage rather than a known gap,
these restricted datasets should each have an access/usage policy.

**How to fix:** In `ontologies/mi-governance.ttl`, add `odrl:Set` policies modelled
on the existing `mi:ChildProfileDataPolicy` / `mi:EmployeeDataPolicy`:
- `mi:CDAIncidentDataPolicy` — read by `mi:CDADirector`; prohibit external distribute.
- `mi:RDPrototypeDataPolicy` — read by `mi:RDDirector`.
- A policy for `mi:CDAComplianceReports` (read by `mi:CDADirector`).
Then add `mi:<Dataset> mi:governedByPolicy mi:<Policy> .` for each.

**Acceptance:** `make query-gov` → **GV6 returns 0 rows**; GV4 lists the new
policies. `make all` still green. (Use real W3C ODRL terms — see item 8.)

---

## 5. CN2 — the one unenforced principle (`Prin_JoyOverFear`)  ·  Priority: Low

**What:** `make query-con` → **CN2** returns 1 row: `Prin_JoyOverFear` has no
`mi:enforcedByShape`/`mi:enforcedByQuery`, so it is aspirational (correctly flagged
by the defensibility audit).

**Why it matters:** Culture principles are intrinsically hard to make machine-
enforceable; today this is honestly surfaced as a gap. Optional to close.

**How to fix (if desired):** Bind it to a measurable proxy. A
`mi:WellbeingPulse`-based query already exists (HC5). Add to
`ontologies/mi-constitution.ttl`:
`mi:Prin_JoyOverFear mi:enforcedByQuery "HC5" .` (or author a dedicated query that
checks the joy-based culture is improving, e.g. ComedyNPS trend) and link it.

**Acceptance:** `make query-con` → **CN2 returns 0 rows**; CN1 shows the binding.

---

## 6. Gate `make materialize` into CI  ·  Priority: Low

**What:** `make materialize` (the R2RML execution test) is opt-in and NOT part of
`make all`, because it needs heavy optional deps (morph-kgc, SQLAlchemy, pandas,
duckdb) pulled via `uv run --with`.

**Why it matters:** The R2RML mapping is only validated when someone remembers to
run `make materialize`; a regression in the mapping could land without CI catching it.

**How to fix:** Add an optional dependency group to `pyproject.toml`, e.g.
```
[dependency-groups]
r2rml = ["morph-kgc", "sqlalchemy"]
```
then either change the `materialize` target to `uv run --group r2rml python …` and
add `materialize` to the `all` target, or add a separate CI job that runs
`make materialize`. Trade-off: `make all` becomes slower and pulls the heavy deps.

**Verify:** `make all` (with materialize folded in) green end-to-end.

---

## 7. Publish to a Git remote + open a PR  ·  Priority: As needed

**What:** The repo is local-only (`git remote -v` is empty), so the `/review`
slash command had no PR to run against and `gh` cannot operate.

**How to fix:** `gh repo create <name> --private --source=. --remote=origin --push`
(or add an existing remote), then open a PR for the work on `main`. `make all` +
`make materialize` should be the PR's check gate.

---

## 8. Use canonical W3C ODRL action terms  ·  Priority: Low (nicety)

**What:** `ontologies/mi-governance.ttl` uses `odrl:read` as an action. `odrl:distribute`
is a standard ODRL action; `odrl:read` is widely used in examples but is not a core
ODRL 2.2 action term.

**Why it matters:** Purely semantic accuracy — nothing in this project validates
against the ODRL action vocabulary, so it does not break any build.

**How to fix (if you want strict ODRL):** replace `odrl:read` with `odrl:use` (the
core "use" action) or define a local sub-action `mi:read rdfs:subPropertyOf odrl:use`
(actions are usually modelled as instances of `odrl:Action`; define
`mi:read a odrl:Action ; rdfs:subClassOf …` per your chosen ODRL profile). Then
update the GV4 query if the action localname changes.

**Verify:** `make query-gov` (GV4 still lists the rules); `make all` green.

---

## Quick reference — verification commands

```bash
make all          # seed → ontology → validate → tests → all 6 query suites (green)
make validate     # exactly 3 intentional violations, named
make test         # 7 detector unit tests
make materialize  # R2RML executed against SQLite, 6/6 checks (needs --with deps)
make drift        # docs excerpts ↔ source-of-truth (0 drift)
make query-gov    # GV6 = current governance gaps (item 4)
make query-con    # CN2 = current unenforced principles (item 5)
make status       # artifact inventory
```
