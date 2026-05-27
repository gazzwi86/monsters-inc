# Execution Prompt — Monsters, Inc. Enterprise Architecture Project

> **How to use this file:** Paste the content of this prompt into a new Claude Code session (or use `/plan` then execute) to generate all remaining project artifacts. The spec and overview are already created. This prompt is fully self-contained — no prior context is needed.

---

## Framing

You are building a comprehensive enterprise architecture reference project for **Monsters, Inc.** — the Pixar fictional energy company. Two files already exist:

- `spec.md` — full project specification (read this first, it is your source of truth)
- `docs/00-overview.md` — enterprise context, six pillars, domain landscape (already approved)

Your task: generate all remaining 12 documentation files, all semantic RDF/Turtle artifacts, the Python/UV project, and the README. Work through them in the order listed below.

**Reasoning disciplines to apply throughout:**

1. **First principles:** For each modeling standard, start from what the standard fundamentally represents (what real-world thing is it modeling?) before writing syntax.
2. **Chain of thought:** Trace how entities and processes in Monsters, Inc. actually connect before committing to class hierarchies or process flows.
3. **Consequential thinking:** Before finalising each artifact, ask — if a modeler changed this, what else would break? Are the cross-references consistent?

---

## Documentation Principles (apply to every file)

These are non-negotiable constraints on how every document and script must be written:

**Diagram-first.** Every document opens with a diagram before any prose. If a concept can be shown, show it. Aim for at least 2 PlantUML diagrams per document. Prose is for "why this matters" and navigation only — not explanation of what the diagram already shows.

**Runnable, not just readable.** Every document that has a corresponding `make` target must include a "Run it" callout box near the top:

```markdown
> **Run it:** `make <target>` — expected output: [one line describing what the table/report shows]
```

**Rich terminal output.** All Python scripts must use `rich` for output: tables with headers, coloured status indicators, and a summary line. No raw `print()` dumps. The user should be able to run `make query` and immediately read the results without interpretation.

**Minimal prose.** Each document section should have: 1 diagram + 1 code artifact + max 3 sentences of explanation. No paragraphs. Use tables instead of bullet lists where structure applies.

**Self-contained navigation.** Every document starts with a nav bar: `[← prev doc] | [→ next doc] | [Run: make target] | [All Views →](../README.md)`

---

## Domain Knowledge (authoritative — use these facts throughout)

### Company Facts
- **Monsters, Inc.** — Monstropolis-based clean energy company
- Formerly collected scream energy; now collects laughter energy (10x more potent: ~14.5 MWh/laugh canister vs ~1.2 MWh/scream canister)
- ~1,200 employees; 100 active comedy stations on the Laugh Floor; two shifts per day
- Regulated by the **CDA (Child Detection Agency)** — cross-dimensional regulatory body
- Energy sold to **Monstropolis Power Grid Authority**
- Recruitment pipeline from **Monsters University**
- Base currency: Monstropolis Energy Credits (MEC)

### Key People (use as named instances in ontology and data files)
| Name | Role | Domain |
|------|------|--------|
| James P. "Sulley" Sullivan | CEO / Top Comedian | D2 |
| Mike Wazowski | Chief Comedy Officer | D2, D6 |
| Roz (Agent 001) | CDA Director (external) | D5 |
| Henry J. Waternoose III | Former CEO (retired/removed) | — |
| Randall Boggs | Former Scarer (terminated) | — |
| Needleman | Senior Door Technician | D3 |
| Smitty | Door Technician | D3 |
| Celia Mae | Head of Guest Relations | D4 |
| Fungus | Lab Assistant, R&D | D6 |
| Jerry (Jerry Vienneau) | Laugh Floor Dispatcher | D2 |

### Six Domains (use these URIs throughout: `https://vocab.monstersinc.com/`)
| ID | Name | URI | Owner |
|----|------|-----|-------|
| D1 | Energy Production | `mi:EnergyProduction` | VP Energy |
| D2 | Laugh Operations | `mi:LaughOperations` | CCO Mike Wazowski |
| D3 | Door Management & Logistics | `mi:DoorManagement` | VP Logistics |
| D4 | HR & Training | `mi:HRTraining` | Chief People Officer |
| D5 | CDA Compliance & Safety | `mi:CDACompliance` | CDA Liaison Officer |
| D6 | R&D — Laughter Initiative | `mi:RDLaughter` | CCO Mike Wazowski |

### Seven Processes
| ID | Name | Domains | Trigger | Outcome |
|----|------|---------|---------|---------|
| P1 | Daily Laugh Run | D2, D3, D1 | ShiftStartEvent | Energy canisters processed, EnergyLedger updated |
| P2 | Door Dispatch & Return | D3, D2 | PortalActivationRequest | Door activated, returned, maintenance logged |
| P3 | Energy Processing & Distribution | D1 | CanisterFilledEvent | MWh units on city grid |
| P4 | Comedian Onboarding & Certification | D4, D2 | NewHireEvent | CertifiedComedian |
| P5 | CDA Incident Response (2319 Protocol) | D5, D2, D3 | ContaminationAlert | IncidentReport, DoorStatusUpdate |
| P6 | Monthly Performance Review | D4, D2, D1 | MonthEndEvent | PerformanceReport, LadderDecision |
| P7 | R&D Prototype Testing | D6, D2 | QuarterlyResearchCycle | PrototypeResult, TechniqueApproval |

### Twelve Core OWL Classes
Use base URI `https://vocab.monstersinc.com/ontology#` (prefix `mi:`)

| Class | Key Properties | Domain |
|-------|---------------|--------|
| `mi:Monster` | `mi:employeeId` (xsd:string), `mi:name` (xsd:string), `mi:role` (mi:Role), `mi:department` (mi:Domain) | Cross |
| `mi:Comedian` (subclass of Monster) | `mi:certLevel` (xsd:integer 1–5), `mi:currentLaughScore` (xsd:decimal), `mi:assignedStation` (mi:LaughFloorStation) | D2,D4 |
| `mi:DoorTechnician` (subclass of Monster) | `mi:clearanceLevel` (xsd:integer), `mi:doorsManaged` (xsd:integer) | D3 |
| `mi:ChildDoor` | `mi:portalCode` (xsd:string, unique), `mi:childProfile` (mi:ChildProfile), `mi:doorStatus` (mi:DoorStatus), `mi:lastMaintained` (xsd:date) | D3 |
| `mi:ChildProfile` | `mi:ageRange` (xsd:string), `mi:bedroomType` (xsd:string), `mi:timezone` (xsd:string) | D3 |
| `mi:LaughCanister` | `mi:capacity` (xsd:decimal, MWh), `mi:fillLevel` (xsd:decimal 0.0–1.0), `mi:energyType` (mi:EnergyType), `mi:sealStatus` (xsd:boolean) | D1,D2 |
| `mi:EnergyUnit` | `mi:megawattHours` (xsd:decimal), `mi:source` (mi:LaughCanister), `mi:generatedAt` (xsd:dateTime), `mi:gridZone` (xsd:string) | D1 |
| `mi:LaughFloorStation` | `mi:stationId` (xsd:string), `mi:assignedComedian` (mi:Comedian), `mi:activeDoor` (mi:ChildDoor), `mi:shift` (mi:Shift) | D2 |
| `mi:CDAIncident` | `mi:incidentCode` (xsd:string, e.g. "2319"), `mi:severity` (xsd:integer 1–5), `mi:reportedAt` (xsd:dateTime), `mi:resolvedAt` (xsd:dateTime), `mi:involvedDoor` (mi:ChildDoor) | D5 |
| `mi:TrainingRecord` | `mi:trainee` (mi:Monster), `mi:program` (mi:TrainingProgram), `mi:completedAt` (xsd:date), `mi:expiresAt` (xsd:date) | D4 |
| `mi:PerformanceRecord` | `mi:comedian` (mi:Comedian), `mi:date` (xsd:date), `mi:laughScore` (xsd:decimal), `mi:energyGenerated` (xsd:decimal, MWh) | D2,D4 |
| `mi:RDPrototype` | `mi:technique` (xsd:string), `mi:yieldTarget` (xsd:decimal, MWh), `mi:testResults` (xsd:string), `mi:status` (mi:PrototypeStatus) | D6 |

### Six Business Rules (SHACL constraints)
1. `ComedianCertShape` — A Comedian must have `mi:certLevel >= 1` before `mi:assignedStation` is set
2. `DoorDispatchShape` — A ChildDoor dispatched must have `mi:doorStatus = "active"` AND `mi:lastMaintained` within 180 days
3. `CanisterTransportShape` — A LaughCanister in transit must have `mi:sealStatus = true`
4. `CDAReportingShape` — A CDAIncident must have `mi:reportedAt` no more than 30 minutes after `mi:detectedAt`
5. `ChildAgeShape` — A ChildDoor must not be dispatched if `mi:ageRange` starts with "13+" (child aged out)
6. `PerformanceRecordShape` — A PerformanceRecord must reference both `mi:comedian` and `mi:date`

### Eight SPARQL Queries
```
Q1: Top 10 comedians by energy yield this month
Q2: Doors with maintenance overdue (>180 days)
Q3: CDA incidents per quarter (last 4 quarters)
Q4: Average laugh-to-energy conversion rate by comedian certification level
Q5: Training certifications expiring in next 30 days
Q6: Monthly energy production trend (last 12 months, MWh)
Q7: Child profiles assigned to more than one door (data integrity)
Q8: Full PROV-O lineage chain for a given EnergyUnit
```

---

## Artifact Generation Instructions

### Standard document structure (apply to every `docs/NN-*.md` file)

```markdown
# [Title] — [View Name]

> **View:** [view type] | **Standard:** [primary standard] | **Audience:** [who reads this]

[2–3 sentence plain-English description of what this view shows and why it matters]

**Navigation:** [← prev] | [→ next] | [All Views →](../README.md)

---

## 1. [Section heading]
[content]

## 2. [Section heading — diagram]
[PlantUML diagram here]

## 3. [Artifact — Turtle/SPARQL/SHACL code block]
[code here with syntax highlighting: ```turtle, ```sparql, ```sql etc.]

## 4. Why this matters
[1–3 sentences on what this view enables — what question it answers]

## 5. Cross-references
[bullet list of related views and how they connect]
```

---

## Document-by-Document Specifications

### `docs/01-domain-model.md` — Domain & Ontology Model

**Standard:** OWL 2 + UML Class Diagram + Turtle  
**Diagrams needed:**
1. PlantUML class diagram showing all 12 OWL classes, key properties, and inheritance (Comedian/DoorTechnician subclass of Monster)
2. Domain partitioning diagram showing which classes belong to which domain

**Turtle artifact:** Write the full `mi-core.ttl` ontology inline as a code block. Include:
- Prefix declarations (`@prefix mi:`, `@prefix owl:`, `@prefix rdfs:`, `@prefix xsd:`)
- OWL ontology header
- All 12 classes as `owl:Class` with `rdfs:label` and `rdfs:comment`
- All key object properties and datatype properties
- Key restrictions: Comedian subClassOf (Monster AND hasProperty certLevel)
- `owl:disjointWith` between Comedian and DoorTechnician
- Domain and range declarations for all properties

**Cross-references:** Links to 02 (capability), 04 (OBPM), 08 (glossary for term definitions), 10 (full graph)

---

### `docs/02-capability-map.md` — Capability Map

**Standard:** ArchiMate 3 (Capability View) via PlantUML  
**Diagrams needed:**
1. Capability heat-map: 6 domains × capability maturity (1–5 scale). Use colour shading to show where Monsters, Inc. is strong vs. developing.
2. ArchiMate-style capability decomposition tree for D2 (Laugh Operations) — the core domain

**Capability inventory to model:**

| Capability | Domain | Maturity | Strategic Importance |
|------------|--------|----------|---------------------|
| Laugh Energy Capture | D2 | 5 | Critical |
| Door Portal Operations | D3 | 4 | Critical |
| Energy Processing | D1 | 4 | Critical |
| CDA Compliance | D5 | 3 | High |
| Comedian Recruitment | D4 | 3 | High |
| Comedian Training & Cert | D4 | 4 | High |
| Laugh Yield Optimisation | D6 | 2 | Growing |
| Laughter Technique R&D | D6 | 2 | Strategic |
| Door Maintenance | D3 | 3 | Supporting |
| Performance Analytics | D2,D4 | 2 | Growing |
| Regulatory Reporting | D5 | 3 | Mandatory |
| Energy Grid Integration | D1 | 4 | Critical |

**Cross-references:** 00 (domain landscape), 07 (service catalog realises capabilities)

---

### `docs/03-business-process.md` — Business Process Model (P1: Daily Laugh Run)

**Standard:** BPMN-style via PlantUML Activity Diagram with swim lanes  
**Swim lanes:** Dispatcher (D2), Comedian (D2), Door Technician (D3), Energy Station (D1), CDA Monitor (D5)

**Process steps to model (in order):**
1. DISPATCHER: Shift start → issue door activation requests for 100 stations
2. DOOR TECH: Retrieve door from vault → quality check → install at station
3. COMEDIAN: Brief (door code, child profile, technique guidance) → enter child's room
4. COMEDIAN: Perform comedy routine → laugh energy captured in canister
5. COMEDIAN: Return through door with sealed canister
6. ENERGY STATION: Receive canister → scan → extract energy → log EnergyUnit
7. DOOR TECH: Remove door from station → log return → return to vault → schedule maintenance
8. CDA MONITOR: Automated compliance check per station → flag any anomalies
9. DISPATCHER: Close shift → aggregate performance data → trigger PerformanceRecord creation

**Exception flows to include:**
- Door quality check fails → door quarantined → replacement requested
- CDA contamination alert → 2319 Protocol triggered (subprocess reference to P5)
- Comedian below minimum laugh threshold → station paused → supervisor intervention

**Turtle artifact:** A short `mi-process.ttl` snippet showing P1 modeled as a `mi:BusinessProcess` with `mi:hasStep` relationships and `mi:triggeredBy`/`mi:produces` object properties.

---

### `docs/04-ontology-bpm.md` — Ontology-Annotated Business Process (OBPM)

**Standard:** OWL 2 + BPMN-O + Turtle  
**What OBPM means:** Each activity in P1 is annotated with the OWL class/individual it creates, modifies, or consumes. This closes the gap between "a process step happened" and "what semantic entity changed as a result."

**Diagrams needed:**
1. Annotated version of the P1 swim lane where each activity box includes `[creates: X]`, `[consumes: Y]`, `[transitions: Z.state]`
2. Ontological annotation legend showing how OWL classes map to BPMN task types (Abstract task, User task, Service task, Subprocess)

**Key OBPM annotations for P1:**
- "Issue door activation request" → `prov:Activity`, produces `mi:PortalActivationRequest`, `prov:used` by Dispatcher Monster
- "Capture laugh energy" → creates `mi:LaughCanister` instance, sets `mi:fillLevel = 1.0`, `mi:sealStatus = false`
- "Seal canister" → transitions `mi:LaughCanister.sealStatus = true`, `prov:wasGeneratedBy` this activity
- "Extract energy" → creates `mi:EnergyUnit`, `prov:wasDerivedFrom` LaughCanister
- "Log PerformanceRecord" → creates `mi:PerformanceRecord` linking comedian + date + laughScore + energyGenerated

**Turtle artifact:** OBPM annotation snippet — show 3 activities from P1 fully annotated using:
- BPMN-O (`bpmn:Task`, `bpmn:Activity`)
- PROV-O (`prov:Activity`, `prov:wasGeneratedBy`, `prov:used`)
- Domain ontology (`mi:LaughCanister`, `mi:EnergyUnit`)

**Cross-references:** 03 (base process), 01 (OWL classes), 06 (lineage — PROV-O continues here)

---

### `docs/05-data-catalog.md` — Data Catalog

**Standard:** DCAT 3 (W3C) + Turtle  
**Dataset inventory (model all 10):**

| Dataset | Description | Format(s) | Owner Domain | Update Freq |
|---------|-------------|-----------|--------------|-------------|
| `mi:MonsterRegistry` | All monster employees, roles, credentials | RDF/Turtle, JSON-LD | D4 | Real-time |
| `mi:DoorInventory` | 10M+ child doors, portal codes, status | RDF/Turtle, Parquet | D3 | Daily |
| `mi:PerformanceRecords` | Daily comedian performance data (laugh scores, MWh) | RDF/Turtle, CSV | D2 | Daily |
| `mi:EnergyLedger` | Energy unit production and grid dispatch log | RDF/Turtle, TimeSeries | D1 | Real-time |
| `mi:CDAIncidentLog` | All 2319 incidents and outcomes | RDF/Turtle, JSON | D5 | On-event |
| `mi:TrainingRegistry` | Certification records, expiry dates | RDF/Turtle, JSON | D4 | On-event |
| `mi:ChildProfiles` | Door-linked child demographic profiles (anonymised) | RDF/Turtle, JSON | D3 | On door-assign |
| `mi:RDPrototypes` | R&D technique experiments and results | RDF/Turtle, JSON | D6 | Quarterly |
| `mi:CDAComplianceReports` | Monthly CDA audit submissions | PDF, RDF/Turtle | D5 | Monthly |
| `mi:EnergyGridForecast` | Demand forecasts from Monstropolis Grid Authority | CSV, JSON | D1 | Weekly |

**Turtle artifact:** Full `mi-catalog.ttl` using `dcat:Catalog`, `dcat:Dataset`, `dcat:Distribution`, `dcat:DataService`. Include:
- One `dcat:Catalog` as the Monsters, Inc. Enterprise Data Catalog
- Three fully specified `dcat:Dataset` entries (MonsterRegistry, DoorInventory, EnergyLedger) with `dcat:distribution`, `dct:description`, `dct:publisher`, `dct:modified`, `dcat:theme`, `dcat:keyword`
- One `dcat:DataService` (the SPARQL endpoint serving the RDF datasets)
- `dcat:DatasetSeries` for PerformanceRecords (daily slices)

**Cross-references:** 06 (lineage of EnergyLedger), 11 (DB schema that feeds DoorInventory), 12 (CDAComplianceReports as unstructured docs)

---

### `docs/06-data-lineage.md` — Data Lineage

**Standard:** PROV-O (W3C) + Turtle  
**Lineage chain to model (end-to-end for a single EnergyUnit):**

```
ChildLaugh (Entity)
  └─wasGeneratedBy─> LaughCollectionActivity
      └─wasAssociatedWith─> Comedian:Sulley
      └─used─> LaughFloorStation:Station-042
                └─used─> ChildDoor:DOOR-NYC-4821
                    └─wasGeneratedBy─> DoorManufacturingActivity
          └─wasInformedBy─> ShiftStartActivity
LaughCanister:CAN-20240315-042 (Entity)
  └─wasDerivedFrom─> ChildLaugh
  └─wasGeneratedBy─> CanisterSealingActivity
EnergyExtractionActivity
  └─used─> LaughCanister:CAN-20240315-042
  └─wasAssociatedWith─> Agent:EnergyProcessingPlant
EnergyUnit:EU-20240315-042-001 (Entity)
  └─wasDerivedFrom─> LaughCanister:CAN-20240315-042
  └─wasGeneratedBy─> EnergyExtractionActivity
GridDispatchActivity
  └─used─> EnergyUnit:EU-20240315-042-001
  └─wasAssociatedWith─> Agent:MonstropolisGridAuthority
```

**Diagrams needed:**
1. PROV-O graph rendered as PlantUML object/dependency diagram (nodes = entities/activities/agents, edges = PROV-O relationships labelled)
2. Simplified lineage swimlane showing temporal flow from laugh to grid

**Turtle artifact:** Full `mi-provenance.ttl` for one complete lineage chain above. Include all PROV-O relationships, timestamps (use xsd:dateTime), and agents. Show how the `prov:Bundle` wraps the entire chain for "provenance of the provenance."

**Cross-references:** 04 (OBPM creates these PROV activities), 05 (EnergyLedger dataset holds these units), 09 (SPARQL Q8 queries this chain)

---

### `docs/07-service-catalog.md` — Service Catalog

**Standard:** ArchiMate 3 (Application & Technology Layers) via PlantUML  
**Services to model:**

**Application Services (Business-facing)**
| Service | Capability Served | Consumer |
|---------|------------------|---------|
| Laugh Floor Management System (LFMS) | D2 core operations | Dispatchers, Comedians |
| Door Portal Control System (DPCS) | D3 dispatch & return | Door Techs, Dispatchers |
| Energy Ledger Service (ELS) | D1 energy accounting | Finance, Grid Authority |
| HR & Certification Platform (HRCP) | D4 people management | HR, Floor Managers |
| CDA Compliance Gateway (CDACG) | D5 regulatory | CDA, Compliance Officers |
| R&D Lab Management System (RDLMS) | D6 research | Scientists, CCO |

**Technology Services (Infrastructure)**
| Service | Purpose |
|---------|---------|
| Portal Network Controller | Routes 10M+ door portal connections |
| Energy Grid Integration API | Real-time MWh dispatch to Monstropolis Grid Authority |
| RDF Knowledge Graph Store | Semantic data layer (all ontologies + instances) |
| SPARQL Query Service | Business intelligence queries |
| CDA Incident API | Regulatory data exchange with external CDA |
| Event Streaming Bus | ShiftStartEvent, CanisterFilledEvent, ContaminationAlert |

**Diagrams needed:**
1. ArchiMate application layer: services, components, and interfaces
2. Technology layer: infrastructure services and their realisation
3. Dependency map: which application services depend on which technology services

**Cross-references:** 02 (capabilities realised by these services), 05 (datasets served by ELS and HRCP)

---

### `docs/08-glossary.md` — Controlled Vocabulary & Glossary

**Standard:** SKOS (W3C) + Turtle  
**Concept scheme URI:** `https://vocab.monstersinc.com/glossary`

**Required concepts (minimum 40):**

Core energy concepts: `LaughEnergy`, `ScreamEnergy` (deprecated), `EnergyCanister`, `EnergyYield`, `MegawattHour`, `LaughConversionRate`, `EnergyLedger`, `GridDispatch`

Operations concepts: `LaughFloor`, `ComedyStation`, `ShiftRun`, `DoorDispatch`, `PortalActivation`, `CanistreSeal`, `ShiftDispatcher`, `PerformanceRecord`, `LaughScore`

Door & portal concepts: `ChildDoor`, `PortalCode`, `DoorVault`, `DoorStatus`, `PortalNetwork`, `ChildProfile`, `DoorMaintenance`, `DoorDecommission`

People & HR concepts: `Comedian`, `DoorTechnician`, `ComedyCertification`, `CertificationLevel`, `TrainingProgram`, `PerformanceLadder`, `FloorManager`

Compliance concepts: `CDAIncident`, `Protocol2319`, `ContaminationAlert`, `DecontaminationUnit`, `ComplianceAudit`, `RegulatoryReport`

R&D concepts: `ComedyTechnique`, `LaughPrototype`, `YieldOptimisation`, `RDCycle`

**SKOS requirements per concept:**
- `skos:prefLabel` (English)
- `skos:definition` (1–2 sentences)
- `skos:broader` / `skos:narrower` where applicable
- `skos:related` for associative links
- `skos:altLabel` for synonyms/abbreviations
- `skos:historyNote` for deprecated terms (ScreamEnergy, ScareFloor)

**Turtle artifact:** Full `mi-glossary.ttl` — complete SKOS concept scheme with all 40+ concepts and all required properties.

**Diagram:** SKOS hierarchy rendered as PlantUML tree — showing `skos:broader` relationships among the ~40 concepts, grouped by top concept.

---

### `docs/09-constraints-queries.md` — Constraints & Business Queries

**Standard:** SHACL (W3C) + SPARQL  
**Two separate artifacts:**

#### Part A — SHACL Shapes

Write all 6 shapes from the spec as fully valid SHACL Turtle:

For each shape include:
- `sh:targetClass`
- `sh:property` with `sh:path`, `sh:minCount`/`sh:maxCount`, `sh:datatype`/`sh:class`
- `sh:message` (human-readable violation message)
- `sh:severity` (sh:Violation or sh:Warning)
- At least 2 shapes must use `sh:constraint` with SPARQL (`sh:sparql` + `sh:select`)

Shape detail for the two SPARQL-based shapes:
- **CDAReportingShape SPARQL:** SELECT where `mi:reportedAt - mi:detectedAt > 30 minutes` — violation
- **ComedianCertShape SPARQL:** SELECT where comedian has `mi:assignedStation` but no valid `mi:TrainingRecord` with `mi:expiresAt > now`

#### Part B — SPARQL Queries

Write all 8 queries from the spec as fully valid SPARQL 1.1. For each query:
- Include `PREFIX` declarations
- Use the `mi:` ontology classes and properties from the domain model
- Add a `# Business question:` comment header
- Show expected result columns in a `# Returns:` comment

Query highlights requiring special attention:
- Q8 (lineage) must navigate the PROV-O chain using property paths
- Q3 (quarterly incidents) must use `BIND` to compute quarter from `xsd:dateTime`
- Q4 (conversion rate by cert level) must use `GROUP BY` and `AVG`

**Diagram:** Visual representation of the SHACL validation flow — PlantUML sequence diagram showing: data instance → SHACL validator → validation report → violation list.

**Cross-references:** 01 (classes that shapes target), 06 (Q8 queries the PROV-O graph), 11 (R2RML produces the data these shapes validate)

---

### `docs/10-entity-graph.md` — Entity Relationship & RDF Graph

**Standard:** OWL + UML + RDF graph notation  
**Diagrams needed:**

1. **Full UML class diagram** (PlantUML) — all 12 classes with ALL properties shown, inheritance arrows, associations with cardinalities:
   - `LaughFloorStation "1" --> "0..1" Comedian : assignedComedian`
   - `LaughFloorStation "1" --> "0..1" ChildDoor : activeDoor`
   - `Comedian "1" --> "*" PerformanceRecord : hasRecord`
   - `ChildDoor "1" --> "1" ChildProfile : childProfile`
   - `LaughCanister "1" --> "1" EnergyUnit : produces`
   - etc.

2. **RDF graph fragment** (PlantUML object diagram) — 5–6 concrete instances from a single shift showing all triple relationships between them (e.g., Sulley the Comedian → Station-042 → Door DOOR-NYC-4821 → ChildProfile → LaughCanister → EnergyUnit)

3. **OWL restriction diagram** — showing key `owl:Restriction` patterns used (e.g., `Comedian subClassOf (hasProperty certLevel some xsd:integer)`)

**Cross-references:** 01 (classes defined), 04 (instances created by processes), 11 (these entities map from DB tables)

---

### `docs/11-db-schema.md` — Relational Database Schema & R2RML Mapping

**Standard:** SQL + R2RML + PlantUML ER diagram  
**Three tables to model:**

```sql
-- Table 1: COMEDIAN
CREATE TABLE COMEDIAN (
    comedian_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    cert_level INTEGER CHECK (cert_level BETWEEN 1 AND 5),
    laugh_score DECIMAL(5,2),
    station_id VARCHAR(20),
    department_id VARCHAR(10),
    hire_date DATE,
    is_active BOOLEAN DEFAULT TRUE
);

-- Table 2: CHILD_DOOR
CREATE TABLE CHILD_DOOR (
    portal_code VARCHAR(30) PRIMARY KEY,
    child_age_range VARCHAR(10) NOT NULL,
    bedroom_type VARCHAR(50),
    door_status VARCHAR(20) CHECK (door_status IN ('active','quarantined','maintenance','decommissioned')),
    last_maintained DATE,
    assigned_comedian_id VARCHAR(20),
    timezone VARCHAR(50),
    FOREIGN KEY (assigned_comedian_id) REFERENCES COMEDIAN(comedian_id)
);

-- Table 3: PERFORMANCE_RECORD
CREATE TABLE PERFORMANCE_RECORD (
    record_id VARCHAR(30) PRIMARY KEY,
    comedian_id VARCHAR(20) NOT NULL,
    record_date DATE NOT NULL,
    laugh_score DECIMAL(5,2),
    energy_generated_mwh DECIMAL(8,4),
    station_id VARCHAR(20),
    shift VARCHAR(10) CHECK (shift IN ('AM','PM')),
    FOREIGN KEY (comedian_id) REFERENCES COMEDIAN(comedian_id)
);
```

**R2RML Turtle artifact:** Full `mi-db.r2rml.ttl` mapping all three tables. Include:
- `rr:TriplesMap` for each table
- `rr:LogicalTable` with `rr:tableName`
- `rr:SubjectMap` with `rr:template` constructing IRIs from primary keys
- `rr:PredicateObjectMap` for each column → RDF property
- `rr:class` assertions (`mi:Comedian`, `mi:ChildDoor`, `mi:PerformanceRecord`)
- `rr:parentTriplesMap` with `rr:joinCondition` for the foreign key relationships
- `rr:R2RMLView` with custom SQL for at least one computed property (e.g., `DATEDIFF(NOW(), last_maintained) AS days_since_maintenance`)

**Diagrams:**
1. PlantUML ER diagram showing the three tables and their FK relationships
2. R2RML mapping flow diagram: `SQL Table → TriplesMap → RDF Triple Pattern`

**Cross-references:** 10 (entity model these tables persist), 09 (SHACL validates the resulting RDF)

---

### `docs/12-unstructured-docs.md` — Unstructured Document Model

**Standard:** OWL document ontology + DCAT + PlantUML  
**Document types to model:**

| Document | Type | Format | Created by Process | Domain |
|----------|------|--------|-------------------|--------|
| CDA Incident Form (2319) | `mi:CDAIncidentForm` | PDF | P5 | D5 |
| Scare/Laugh Run Shift Report | `mi:ShiftReport` | PDF/JSON | P1 | D2 |
| Comedian Certification Letter | `mi:CertificationDocument` | PDF | P4 | D4 |
| R&D Prototype Test Report | `mi:PrototypeTestReport` | PDF/Markdown | P7 | D6 |
| Monthly CDA Compliance Submission | `mi:ComplianceSubmission` | PDF/RDF | P6 (compliance) | D5 |
| Door Maintenance Log | `mi:MaintenanceLog` | JSON/PDF | P2 | D3 |

**OWL document ontology to create (inline Turtle):**
- Superclass `mi:BusinessDocument` with properties: `mi:createdAt`, `mi:createdBy`, `mi:relatesTo`, `mi:documentStatus`, `mi:mimeType`
- Each document type as a subclass with its specific required fields
- Link to DCAT: each `mi:BusinessDocument` is also a `dcat:Distribution` of a `dcat:Dataset`
- Link to PROV-O: each document `prov:wasGeneratedBy` a named process activity

**Diagram:**
1. OWL class hierarchy of document types (PlantUML class diagram)
2. Document lifecycle state machine (PlantUML state diagram): `Draft → Submitted → Approved → Archived → Destroyed`

**Cross-references:** 04 (OBPM creates documents), 05 (DCAT catalog includes these), 06 (PROV-O traces document generation)

---

## Python / UV Project Instructions

### `pyproject.toml`
```toml
[project]
name = "monsters-inc-enterprise-model"
version = "0.1.0"
description = "Enterprise architecture artifacts for Monsters, Inc. using open semantic web standards"
requires-python = ">=3.11"
dependencies = [
    "rdflib>=7.0.0",
    "pyshacl>=0.26.0",
    "rich>=13.0.0",
    "typer>=0.12.0",
]

[project.scripts]
mi-ontology = "scripts.generate_ontology:main"
mi-validate = "scripts.validate_shacl:main"
mi-query = "scripts.run_queries:main"
mi-catalog = "scripts.build_catalog:main"
mi-seed = "scripts.seed_data:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### `scripts/generate_ontology.py`
- Uses `rdflib` to programmatically construct all 12 OWL classes and their properties
- Outputs to `ontologies/mi-core.ttl` (Turtle serialization)
- Also generates `mi-domain.ttl`, `mi-glossary.ttl`
- Prints a rich summary table: "Class | Properties | Axioms"

### `scripts/validate_shacl.py`
- Loads `ontologies/mi-core.ttl` + `data/monsters.json` (converted to RDF) + `shapes/mi-core.shacl.ttl`
- Runs `pyshacl.validate()`
- Prints violations as a formatted table using `rich`
- Intentionally includes 2 violations in seed data to demonstrate the validator

### `scripts/run_queries.py`
- Loads all ontology Turtle files into a single `rdflib.ConjunctiveGraph`
- Executes all 8 SPARQL queries from `queries/business-questions.sparql`
- Prints results as formatted tables using `rich`
- Accepts `--query Q1` argument to run a single query

### `scripts/seed_data.py`
- Populates a `rdflib.Graph` with ~25 Monster instances, ~50 Door records, ~100 PerformanceRecords
- Includes Sulley, Mike, Roz, Needleman, Smitty as named instances
- Intentionally violates 2 SHACL constraints (one comedian without cert, one door with stale maintenance)
- Serialises to `data/seed_graph.ttl`

### `scripts/build_catalog.py`
- Reads `data/` folder for JSON files
- Generates DCAT entries for each data asset
- Appends to `ontologies/mi-catalog.ttl`

### `Makefile`

All targets must print a header line before running so the user knows what they're seeing:
```
@echo "──────────────────────────────────────────"
@echo "  Monsters, Inc. — [Target Name]"
@echo "──────────────────────────────────────────"
```

```makefile
.PHONY: all ontology validate query catalog seed demo tour install

# Full build: seed data → generate ontology → validate → run all queries
all: seed ontology validate query
	@echo "✓ All artifacts built and verified"

# Run the full guided demo in sequence (for the runbook walkthrough)
demo: install seed ontology
	@echo "Demo data loaded. Run 'make query' or 'make Q=Q1 query-one' to explore."

# Run a single query: make Q=Q1 query-one
query-one:
	@echo "Running query $(Q)..."
	uv run mi-query --query $(Q)

ontology:
	@echo "── Generating OWL ontology ──"
	uv run mi-ontology

seed:
	@echo "── Seeding instance data ──"
	uv run mi-seed

validate:
	@echo "── SHACL validation (expect 2 violations) ──"
	uv run mi-validate

query:
	@echo "── Running all 8 SPARQL queries ──"
	uv run mi-query

catalog:
	@echo "── Building DCAT catalog ──"
	uv run mi-catalog

install:
	uv sync

# Show artifact build status
status:
	@echo "── Artifact progress ──"
	@printf "  docs:       %2s/13\n"  "$$(find docs -name '*.md' 2>/dev/null | wc -l | tr -d ' ')"
	@printf "  ontologies: %2s/6\n"   "$$(find ontologies -name '*.ttl' 2>/dev/null | wc -l | tr -d ' ')"
	@printf "  shapes:     %2s/2\n"   "$$(find shapes -name '*.ttl' 2>/dev/null | wc -l | tr -d ' ')"
	@printf "  mappings:   %2s/1\n"   "$$(find mappings -name '*.ttl' 2>/dev/null | wc -l | tr -d ' ')"
	@printf "  queries:    %2s/2\n"   "$$(find queries -name '*.sparql' 2>/dev/null | wc -l | tr -d ' ')"
	@printf "  scripts:    %2s/5\n"   "$$(find scripts -name '*.py' 2>/dev/null | wc -l | tr -d ' ')"
```

---

## Semantic Artifact Content Requirements

### `ontologies/mi-core.ttl`
Full OWL 2 ontology. Must include:
- Ontology URI: `https://vocab.monstersinc.com/ontology`
- 8 prefixes: `mi:`, `owl:`, `rdf:`, `rdfs:`, `xsd:`, `skos:`, `prov:`, `dcat:`
- All 12 classes
- All properties with domain/range
- 3 key restrictions (Comedian, ChildDoor dispatch rule, LaughCanister seal)
- `owl:disjointWith` between Comedian and DoorTechnician

### `shapes/mi-core.shacl.ttl`
All 6 SHACL shapes. Must be valid SHACL 1.0. Include `sh:NodeShape` for each class.

### `shapes/mi-compliance.shacl.ttl`
CDA-specific shapes. At least 3 shapes covering incident reporting, door contamination, and canister handling. Must use `sh:severity sh:Violation` for regulatory requirements.

### `mappings/mi-db.r2rml.ttl`
Full R2RML mapping of all 3 SQL tables. Must include join conditions for FK relationships.

### `queries/business-questions.sparql`
All 8 queries, one per named graph/section. Use SPARQL 1.1 features.

### `queries/compliance-violations.sparql`
3 queries that mirror the SPARQL-based SHACL constraints — detecting violations in the data directly.

---

## README.md Requirements

README is the first thing opened. It must be **visual and navigable in under 2 minutes**. Keep prose to a minimum — links, tables, and one-liner descriptions only.

```markdown
# Monsters, Inc. Enterprise Architecture

> A complete open-standards enterprise model of Monsters, Inc. (Pixar) — demonstrating OWL 2,
> SKOS, SHACL, SPARQL, PROV-O, DCAT 3, R2RML, and ArchiMate.
> Built to show the direction of travel for MS IQ.

## Quick Start

\`\`\`bash
uv sync        # install dependencies
make seed      # load example data (25 monsters, 50 doors, 100 performance records)
make ontology  # generate all .ttl ontology files
make validate  # run SHACL validation — shows 2 intentional violations
make query     # run all 8 SPARQL queries — rich table output
make all       # run everything in sequence
\`\`\`

Single query: `make Q=Q1 query-one`

## The Model at a Glance

[PlantUML diagram — copy the domain landscape from docs/00-overview.md]

## View Map

| # | Document | What it shows | Run it |
|---|----------|--------------|--------|
| 00 | [Overview](docs/00-overview.md) | Context, pillars, domains | — |
| 01 | [Domain Model](docs/01-domain-model.md) | OWL class hierarchy | `make ontology` |
| 02 | [Capability Map](docs/02-capability-map.md) | Capability heat-map | — |
| 03 | [Business Process](docs/03-business-process.md) | Daily Laugh Run swim-lane | — |
| 04 | [Ontology BPM](docs/04-ontology-bpm.md) | Process annotated with OWL | — |
| 05 | [Data Catalog](docs/05-data-catalog.md) | DCAT 3 catalog of all datasets | `make catalog` |
| 06 | [Data Lineage](docs/06-data-lineage.md) | PROV-O laugh→grid chain | `make Q=Q8 query-one` |
| 07 | [Service Catalog](docs/07-service-catalog.md) | ArchiMate tech/app services | — |
| 08 | [Glossary](docs/08-glossary.md) | SKOS 40+ defined terms | — |
| 09 | [Constraints & Queries](docs/09-constraints-queries.md) | SHACL shapes + 8 SPARQL queries | `make validate && make query` |
| 10 | [Entity Graph](docs/10-entity-graph.md) | Full OWL entity-relationship | — |
| 11 | [DB Schema](docs/11-db-schema.md) | SQL tables + R2RML mapping | — |
| 12 | [Unstructured Docs](docs/12-unstructured-docs.md) | Document ontology | — |

## Standards Coverage

| Standard | File(s) | Models |
|----------|---------|--------|
| OWL 2 / Turtle | `ontologies/mi-core.ttl` | All 12 entity classes |
| SKOS | `ontologies/mi-glossary.ttl` | 40+ controlled terms |
| SHACL | `shapes/*.shacl.ttl` | 6 constraint shapes |
| SPARQL 1.1 | `queries/*.sparql` | 8 business + 3 compliance queries |
| PROV-O | `ontologies/mi-provenance.ttl` | Laugh→canister→energy→grid lineage |
| DCAT 3 | `ontologies/mi-catalog.ttl` | 10 dataset catalog entries |
| R2RML | `mappings/mi-db.r2rml.ttl` | 3 SQL tables → RDF |
| ArchiMate 3 | In each `docs/*.md` | PlantUML-rendered views |

## Walkthrough

See [RUNBOOK.md](RUNBOOK.md) for a step-by-step tour: open a diagram → run a command → read the output.
\`\`\`

---

## RUNBOOK.md Requirements

This is the hands-on walkthrough. Each step has exactly three parts: **what to look at**, **what to run**, **what you'll see**. No explanatory prose. Use `>` blockquotes for expected output samples.

```markdown
# Monsters, Inc. — Runbook

Step-by-step tour of the enterprise architecture. Open each diagram, run each command, read the output.

---

## Setup (do this once)

\`\`\`bash
cd /path/to/obpm
uv sync
make seed
make ontology
\`\`\`

---

## Step 1 — The Company in Context
**Open:** [docs/00-overview.md](docs/00-overview.md) — Enterprise Context diagram  
**Shows:** Monsters, Inc. in relation to Human World, CDA, Monstropolis Grid, Monsters University

---

## Step 2 — What the Company Can Do
**Open:** [docs/02-capability-map.md](docs/02-capability-map.md) — Capability heat-map  
**Shows:** 12 capabilities mapped to 6 domains, colour-coded by maturity

---

## Step 3 — How It Works (Core Process)
**Open:** [docs/03-business-process.md](docs/03-business-process.md) — Daily Laugh Run swim-lane  
**Shows:** Dispatcher → Comedian → Door Tech → Energy Station → CDA Monitor

---

## Step 4 — The Data Model
**Open:** [docs/10-entity-graph.md](docs/10-entity-graph.md) — UML class diagram  
**Run:**
\`\`\`bash
make ontology
\`\`\`
> Output: rich table — "Class | Properties | Axioms" — 12 rows, e.g. Comedian | 6 properties | 2 restrictions

---

## Step 5 — Business Questions (SPARQL)
**Open:** [docs/09-constraints-queries.md](docs/09-constraints-queries.md) — Query list  
**Run:**
\`\`\`bash
make query
\`\`\`
> Output: 8 result tables — top comedians, overdue doors, incident trend, energy chart, expiring certs...

Run a single query:
\`\`\`bash
make Q=Q1 query-one   # Top 10 comedians by energy yield
make Q=Q6 query-one   # 12-month energy production trend
make Q=Q8 query-one   # Full PROV-O lineage for an energy unit
\`\`\`

---

## Step 6 — Constraint Violations (SHACL)
**Open:** [docs/09-constraints-queries.md](docs/09-constraints-queries.md) — SHACL section  
**Run:**
\`\`\`bash
make validate
\`\`\`
> Output: violation table — 2 rows. Row 1: Comedian Randall Boggs assigned station without valid cert. Row 2: Door DOOR-NYC-0099 last maintained 210 days ago (limit: 180).

---

## Step 7 — Where the Data Came From (Lineage)
**Open:** [docs/06-data-lineage.md](docs/06-data-lineage.md) — PROV-O graph  
**Run:**
\`\`\`bash
make Q=Q8 query-one
\`\`\`
> Output: lineage chain — Sulley laughs → LaughCanister CAN-20240315-042 → EnergyUnit EU-001 → Monstropolis Grid Zone A

---

## Step 8 — The Data Catalog
**Open:** [docs/05-data-catalog.md](docs/05-data-catalog.md) — DCAT catalog  
**Run:**
\`\`\`bash
make catalog
\`\`\`
> Output: catalog table — 10 datasets, format, owner domain, update frequency

---

## Step 9 — How the Database Maps to RDF
**Open:** [docs/11-db-schema.md](docs/11-db-schema.md) — R2RML mapping diagram  
**Shows:** COMEDIAN → mi:Comedian, CHILD_DOOR → mi:ChildDoor, FK joins → owl:ObjectProperty

---

## Step 10 — Explore the Vocabulary
**Open:** [docs/08-glossary.md](docs/08-glossary.md) — SKOS concept tree  
**Shows:** 40+ terms from LaughEnergy to Protocol2319, with broader/narrower hierarchy

---

## Full Run (everything at once)
\`\`\`bash
make all
\`\`\`
> Runs: seed → ontology → validate → query  
> Total time: ~15 seconds  
> Output: 4 reports in sequence
```

## View Map
[Table linking all 13 docs with one-line descriptions]

## Standards Coverage
[Table: Standard | Artifacts | What it models here]

## Project Structure
[File tree]

## Key Concepts Demonstrated
[Bullet list referencing each of: domain modeling, capability modeling, OBPM, DCAT, PROV-O, SHACL, SPARQL, R2RML, SKOS, ArchiMate]
```

---

## Execution Order

Work through artifacts in this exact sequence to ensure cross-references are correct:

```
1.  README.md (skeleton — fill links as docs are created)
2.  pyproject.toml + Makefile
3.  docs/01-domain-model.md  →  ontologies/mi-core.ttl
4.  docs/08-glossary.md      →  ontologies/mi-glossary.ttl
5.  docs/02-capability-map.md
6.  docs/03-business-process.md  →  ontologies/mi-process.ttl (snippet)
7.  docs/04-ontology-bpm.md
8.  docs/10-entity-graph.md
9.  docs/11-db-schema.md     →  mappings/mi-db.r2rml.ttl
10. docs/09-constraints-queries.md → shapes/mi-core.shacl.ttl
                                   → shapes/mi-compliance.shacl.ttl
                                   → queries/business-questions.sparql
                                   → queries/compliance-violations.sparql
11. docs/06-data-lineage.md  →  ontologies/mi-provenance.ttl
12. docs/05-data-catalog.md  →  ontologies/mi-catalog.ttl
13. docs/07-service-catalog.md
14. docs/12-unstructured-docs.md
15. scripts/seed_data.py     →  data/seed_graph.ttl
16. scripts/generate_ontology.py
17. scripts/validate_shacl.py
18. scripts/run_queries.py
19. scripts/build_catalog.py
20. data/monsters.json + data/doors.json + data/scare_records.json
21. README.md (fill all links and standards table)
22. RUNBOOK.md (written last — all make targets and doc links must exist first)
```

---

## Quality Checklist

Before declaring complete, verify:

- [ ] All PlantUML diagrams are syntactically valid (no unclosed blocks, valid skinparam keys)
- [ ] All Turtle files parse cleanly (`rdflib.Graph().parse(file, format='turtle')` raises no error)
- [ ] All SPARQL queries are syntactically valid (PREFIX, SELECT/CONSTRUCT, WHERE, correct property paths)
- [ ] All SHACL shapes have `sh:targetClass` and at least one `sh:property`
- [ ] R2RML file has at least one `rr:parentTriplesMap` with `rr:joinCondition`
- [ ] Every markdown doc has: frontmatter view/standard/audience block, navigation bar with `make` command, at least 2 PlantUML diagrams, at least one code artifact, "Why this matters" section, cross-references
- [ ] Every doc that has a corresponding `make` target includes a "Run it" callout near the top
- [ ] All Python scripts produce `rich` formatted table output — no raw print() dumps
- [ ] `make query` output is immediately readable without interpretation (column headers, values, summary line)
- [ ] `make validate` output clearly shows the 2 intentional violations with violation message and location
- [ ] RUNBOOK.md exists and each step has: open link + run command + expected output sample
- [ ] README.md has the View Map table with `make` commands, the domain landscape diagram, and a link to RUNBOOK.md
- [ ] Sulley and Mike appear as named instances in seed data and at least 3 diagram examples
- [ ] The six enterprise pillars are each explicitly referenced in at least one document
- [ ] CDA cross-domain concern is visible in D2, D3, and D5 artifacts
- [ ] `make all` completes without error in under 30 seconds
```

## LAW

You HAVE to check this is all working as expected throughout. This means running scripts, viewing files and validating outputs. eg. Runnning and manually testing make commands, viewing markdown files and checking/processeing and comprehending visually the putputs of the documents etc. this may require you to capture things as an image or pdf to visually inspect and comprehend. This could be done by a dedicated agent team member to issolate context.

Use the agent teams as needed to issolate context and create targetted simple outcomes agents can execute on and complete comprehensovely. This will help manage speed and context and token consumption.

Be structured and deliberate:
- Use consiquencial thinking techniques to reflect on important considerations, thinking deeply and hypothosising about the imapacts of approaches
- Use first principles reasonsing, breaking things down into fundamentals
- Use chain of thought reasoning for thinking through the problem and building out a list of tasks to excute against.
- If you are not sure, have doubts, low confidence, ask via MCQ or similar.