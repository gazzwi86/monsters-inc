# Monsters, Inc. — Enterprise Architecture Project Specification

> **MS IQ Direction Note:** This project demonstrates the open-standards modeling capabilities that MS IQ is being designed to support and import. All artifacts are authored in open, interoperable formats (OWL 2, RDF/Turtle, SHACL, SPARQL, PROV-O, DCAT 3, SKOS, R2RML, ArchiMate).

---

## 1. Purpose

Produce a comprehensive, interconnected set of enterprise architecture artifacts for **Monsters, Inc.** — a fictional company from Pixar's *Monsters, Inc.* (2001) and *Monsters University* (2013). The artifacts collectively demonstrate how a modern enterprise can be modeled using the full stack of open semantic web and enterprise architecture standards, going beyond what any single proprietary platform currently provides.

The result is both a **learning resource** (how these standards work and interrelate) and a **demonstration artefact** (the kind of output MS IQ should be able to produce and consume).

---

## 2. Company Profile

| Attribute | Value |
|-----------|-------|
| **Name** | Monsters, Inc. |
| **Industry** | Clean Energy Production |
| **Former Industry** | Scare Energy (fear-based power generation) |
| **Headquarters** | Monstropolis |
| **Founded** | ~1870s (est.) |
| **Employees** | ~1,200 (645 scarers/comedians, 280 door technicians, 180 operations, 95 R&D, 100 administration) |
| **CEO** | James P. "Sulley" Sullivan |
| **Chief Comedy Officer** | Mike Wazowski |
| **Regulatory Body** | Child Detection Agency (CDA) |
| **Energy Customer** | Monstropolis Power Grid Authority |
| **Mission** | Power Monstropolis sustainably through laughter — the world's cleanest, most powerful energy source |
| **Vision** | A world where every laugh powers a city block |

### Business Model Transformation

The company underwent a fundamental pivot after the "2319 Incident":

```
BEFORE (Scare Era)                    AFTER (Laugh Era)
─────────────────────────────────     ─────────────────────────────────
Energy source: Child screams          Energy source: Child laughter
Yield: ~1.2 MWh/scream canister      Yield: ~14.5 MWh/laugh canister
Risk: High (CDA incidents frequent)  Risk: Low (positive interaction)
Culture: Competitive, secretive       Culture: Collaborative, creative
Attrition: 18% scarer turnover/yr    Attrition: 4% comedian turnover/yr
```

---

## 3. The Six Enterprise Pillars

| Pillar | Monsters, Inc. Expression | Key Modeling Artifact |
|--------|--------------------------|----------------------|
| **Strategy** | Pivot from fear → laughter; dominate clean energy market; ethical sourcing mandate | ArchiMate Motivation View, Goal Ontology |
| **Methods** | Laughter collection methodology; door portal operations; energy processing procedures | BPMN-style Process Models, OBPM |
| **People** | 1,200 monsters across 8 roles; career ladder from trainee → floor manager; skills ontology | HR Ontology, Org Chart, Role SHACL shapes |
| **Culture** | Transformation from fear-based competition to joy-based collaboration; psychological safety as operational requirement | Values in SKOS, Culture ontology notes |
| **Technology** | Door portal network (10M+ doors); energy containment grid; laugh floor systems; CDA integration API; training simulators | Service Catalog, ArchiMate Tech View |
| **Operations** | Two laugh-floor shifts/day; 100 active comedy stations; door logistics pipeline; 24/7 energy processing; real-time CDA monitoring | Data Lineage, DCAT catalog, Constraint queries |

---

## 4. Domain Inventory

Six bounded domains, each with a clear owner, data assets, and cross-domain dependencies:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Monsters, Inc. Domains                        │
├──────────────────────┬──────────────────────────────────────────┤
│ D1: Energy Production│ Converting raw energy canisters to       │
│                      │ electrical units; grid distribution       │
├──────────────────────┼──────────────────────────────────────────┤
│ D2: Laugh Operations │ Comedy floor management; shift scheduling;│
│                      │ comedian performance; canister handling    │
├──────────────────────┼──────────────────────────────────────────┤
│ D3: Door Management  │ Door inventory (10M+ portals); portal     │
│    & Logistics       │ code management; maintenance; dispatch    │
├──────────────────────┼──────────────────────────────────────────┤
│ D4: HR & Training    │ Recruitment; comedian certification;      │
│                      │ skills tracking; performance management   │
├──────────────────────┼──────────────────────────────────────────┤
│ D5: CDA Compliance   │ Child contamination protocols; incident   │
│    & Safety          │ response; audit trail; regulatory reports │
├──────────────────────┼──────────────────────────────────────────┤
│ D6: R&D — Laughter   │ New comedy technique research; prototype  │
│    Initiative        │ testing; yield optimisation; IP registry  │
└──────────────────────┴──────────────────────────────────────────┘
```

### Cross-Domain Dependencies

```
D4 (HR) ──[certifies]──────────────> D2 (Operations)
D3 (Doors) ──[supplies doors to]──> D2 (Operations)
D2 (Operations) ──[produces canisters]──> D1 (Energy)
D5 (CDA) ──[regulates]──────────> D2, D3, D1
D6 (R&D) ──[improves techniques of]──> D2 (Operations)
D1 (Energy) ──[funds via revenue]──> D4, D6
```

---

## 5. Process Inventory

| # | Process | Domain(s) | Frequency | Modeling Approach |
|---|---------|-----------|-----------|-------------------|
| P1 | Daily Laugh Run | D2, D3, D1 | Twice daily | BPMN + OBPM |
| P2 | Door Dispatch & Return | D3, D2 | Per shift | Activity Diagram |
| P3 | Energy Processing & Distribution | D1 | Continuous | Data Lineage (PROV-O) |
| P4 | Comedian Onboarding & Certification | D4, D2 | On hire | Sequence Diagram |
| P5 | CDA Incident Response (2319 Protocol) | D5, D2, D3 | On demand | BPMN + Constraint |
| P6 | Monthly Performance Review | D4, D2, D1 | Monthly | SPARQL Query |
| P7 | R&D Prototype Testing | D6, D2 | Quarterly | Process + PROV-O |

---

## 6. Entity Inventory

### Core Entities (OWL Classes)

| Entity | Domain | Key Properties |
|--------|--------|----------------|
| `Monster` | Cross-domain | name, employeeId, role, department |
| `Comedian` | D2, D4 | certificationLevel, laughScore, assignedStation |
| `ChildDoor` | D3 | portalCode, childProfile, maintenanceStatus, lastActivated |
| `LaughCanister` | D1, D2 | capacity, fillLevel, energyType, processingStatus |
| `ScreamCanister` | D1, D2 | (legacy) capacity, fillLevel, processingStatus |
| `EnergyUnit` | D1 | mwh, source, timestamp, gridDestination |
| `LaughFloorStation` | D2 | stationId, comedian, door, shift |
| `CDAIncident` | D5 | incidentType, severity, reportedAt, resolvedAt |
| `TrainingRecord` | D4 | monster, program, completedAt, expiresAt |
| `PerformanceRecord` | D2, D4 | comedian, date, laughScore, energyGenerated |
| `ChildProfile` | D3 | ageRange, bedroomType, timezone, doorAssigned |
| `RDPrototype` | D6 | technique, yieldTarget, testResults, status |

---

## 7. Technology Stack

| Standard | Purpose in this Project | Files |
|----------|------------------------|-------|
| **OWL 2 / Turtle** | Core ontology — classes, properties, restrictions | `ontologies/*.ttl` |
| **SKOS** | Controlled vocabulary & glossary | `ontologies/mi-glossary.ttl` |
| **SHACL** | Constraint validation shapes | `shapes/*.shacl.ttl` |
| **SPARQL** | Business queries & constraint violation detection | `queries/*.sparql` |
| **PROV-O** | Data lineage (energy canister → processed units → grid) | `ontologies/mi-provenance.ttl` |
| **DCAT 3** | Data catalog for all Monsters, Inc. datasets | `ontologies/mi-catalog.ttl` |
| **R2RML** | Mapping operational DB tables to RDF graph | `mappings/mi-db.r2rml.ttl` |
| **ArchiMate 3** | Enterprise architecture views (via PlantUML) | In `docs/` markdown |
| **UML** | Class, sequence, component diagrams (via PlantUML) | In `docs/` markdown |
| **Python / UV** | Code to generate, validate, query, and serve RDF | `scripts/*.py`, `pyproject.toml` |
| **RDFLib** | In-memory RDF graph engine (Python) | dependency |
| **pyshacl** | SHACL validation engine (Python) | dependency |

---

## 8. Artifact List

### Documentation (13 Markdown Files)

| File | Content | Primary Standards |
|------|---------|-------------------|
| `docs/00-overview.md` | Company context map; domain landscape; 6-pillar view | ArchiMate (PlantUML) |
| `docs/01-domain-model.md` | Domain diagram; OWL class hierarchy; bounded contexts | OWL 2, UML |
| `docs/02-capability-map.md` | Capability heat-map; ArchiMate capability view | ArchiMate |
| `docs/03-business-process.md` | P1 Daily Laugh Run — full BPMN-style process | UML Activity |
| `docs/04-ontology-bpm.md` | P1 annotated with OWL concepts (OBPM) | OWL + BPMN |
| `docs/05-data-catalog.md` | DCAT catalog of all 12 data assets | DCAT 3 |
| `docs/06-data-lineage.md` | PROV-O lineage for energy production chain | PROV-O |
| `docs/07-service-catalog.md` | ArchiMate application/technology service view | ArchiMate |
| `docs/08-glossary.md` | SKOS concept scheme; 40+ defined terms | SKOS |
| `docs/09-constraints-queries.md` | 6 SHACL shapes + 8 SPARQL queries | SHACL, SPARQL |
| `docs/10-entity-graph.md` | RDF graph / network diagrams; entity relationship | OWL, UML |
| `docs/11-db-schema.md` | SQL schema (3 tables) + R2RML mapping | R2RML, SQL |
| `docs/12-unstructured-docs.md` | Document ontology for CDA forms & scare reports | OWL, DCAT |
| `README.md` | Navigation hub, view map table, domain diagram, quick-start commands | ArchiMate, Makefile |
| `RUNBOOK.md` | Step-by-step walkthrough: open diagram → run command → read output | Makefile |

### Semantic Artifacts (RDF/Turtle Files)

```
ontologies/
  mi-core.ttl          Core OWL ontology (all 12 classes, 35 properties)
  mi-domain.ttl        Domain partitioning ontology
  mi-process.ttl       Process ontology (annotates P1–P7)
  mi-provenance.ttl    PROV-O instances for energy chain
  mi-catalog.ttl       DCAT 3 catalog
  mi-glossary.ttl      SKOS concept scheme

shapes/
  mi-core.shacl.ttl    Core property + cardinality shapes
  mi-compliance.shacl.ttl  CDA regulatory constraint shapes

mappings/
  mi-db.r2rml.ttl      R2RML mapping for 3 operational tables

queries/
  business-questions.sparql   8 analytical queries
  compliance-violations.sparql  Constraint violation detection
```

### Python / UV Project

```
scripts/
  generate_ontology.py   Writes all .ttl files from Python model
  validate_shacl.py      Runs pyshacl against instance data
  run_queries.py         Executes SPARQL queries, prints results
  build_catalog.py       Generates DCAT catalog from data inventory
  seed_data.py           Populates example RDF instance data

data/
  monsters.json          25 monster instances
  doors.json             50 door records
  scare_records.json     100 performance records (mix of scream/laugh era)

pyproject.toml           UV project; deps: rdflib, pyshacl, SPARQLWrapper
Makefile                 make ontology / make validate / make query / make all
```

---

## 9. File Structure

```
/obpm/
├── README.md                    ← Navigation hub + MS IQ context
├── spec.md                      ← This file
├── PROMPT.md                    ← Execution prompt for full generation
├── Makefile
├── pyproject.toml
├── docs/
│   ├── 00-overview.md
│   ├── 01-domain-model.md
│   ├── 02-capability-map.md
│   ├── 03-business-process.md
│   ├── 04-ontology-bpm.md
│   ├── 05-data-catalog.md
│   ├── 06-data-lineage.md
│   ├── 07-service-catalog.md
│   ├── 08-glossary.md
│   ├── 09-constraints-queries.md
│   ├── 10-entity-graph.md
│   ├── 11-db-schema.md
│   └── 12-unstructured-docs.md
├── ontologies/
│   ├── mi-core.ttl
│   ├── mi-domain.ttl
│   ├── mi-process.ttl
│   ├── mi-provenance.ttl
│   ├── mi-catalog.ttl
│   └── mi-glossary.ttl
├── shapes/
│   ├── mi-core.shacl.ttl
│   └── mi-compliance.shacl.ttl
├── mappings/
│   └── mi-db.r2rml.ttl
├── queries/
│   ├── business-questions.sparql
│   └── compliance-violations.sparql
├── scripts/
│   ├── generate_ontology.py
│   ├── validate_shacl.py
│   ├── run_queries.py
│   ├── build_catalog.py
│   └── seed_data.py
└── data/
    ├── monsters.json
    ├── doors.json
    └── scare_records.json
```

---

## 10. Success Criteria

- [ ] All 13 markdown documents created, internally linked, and self-explaining
- [ ] All PlantUML diagrams syntactically valid (renderable)
- [ ] All Turtle files parse cleanly with `rdflib`
- [ ] All SHACL shapes validate correctly against seed instance data
- [ ] All SPARQL queries execute and return meaningful results
- [ ] R2RML mapping covers at least 3 relational tables
- [ ] Python UV project installs and runs end-to-end (`make all`)
- [ ] The six enterprise pillars are visibly represented across the artifacts
- [ ] Cross-domain dependencies are explicit in at least 3 artifacts
- [ ] Every artifact includes a short "Why this matters" explanation

---

## 11. Domain Knowledge Reference

### Key Characters (Role Instances)
- **Sulley (James P. Sullivan)** — CEO, Top Comedian, D2
- **Mike Wazowski** — Chief Comedy Officer, D6 lead
- **Roz / Agent 001** — CDA Director, D5
- **Randall Boggs** — (former) Scarer, competitor  
- **Henry J. Waternoose III** — Former CEO (removed post-scandal)
- **Needleman & Smitty** — Door Technicians, D3

### Key Business Rules (Seed SHACL Constraints)
1. A Comedian must hold a valid `ComedyCertification` before accessing any ChildDoor
2. A ChildDoor must have status `active` and `maintenanceStatus = OK` before dispatch
3. A LaughCanister must be `sealed` before transport to energy processing
4. A CDAIncident must be reported within 30 minutes of detection
5. A ChildDoor must not be dispatched if the child's age profile exceeds 12 years
6. A PerformanceRecord must reference both a Comedian and a specific LaughFloorStation

### Key SPARQL Questions (Seed Queries)
1. Who are the top 10 comedians by energy yield this month?
2. Which doors have not had maintenance in over 180 days?
3. How many CDA incidents occurred per quarter (last 4 quarters)?
4. What is the average laugh-to-energy conversion rate by comedian class?
5. Which training certifications are expiring in the next 30 days?
6. What is total energy production (MWh) trend over last 12 months?
7. Which child profiles are assigned to more than one door?
8. Show the full provenance chain for a given energy unit (from laugh to grid)
