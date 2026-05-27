# Monsters, Inc. EA — Remediation Plan
**Produced:** 2026-05-27  
**Council:** Ontology/KG Engineer, AI Agent Architect, Enterprise Architect, Business Operations Analyst, Data Engineer, Compliance & Risk Officer, People & Culture Lead  
**Priority order agreed:** Bugs → Standards violations → Gaps (agent model, org, processes, compliance)

---

## Phase 1 — Bug Fixes (Breaking / Incorrect Behaviour)

These must be addressed first. They cause `make query` to return silent empty results or produce structurally incorrect data.

### 1.1 Q8 PROV-O Chain — Broken Query
**Priority:** P1-Critical | **Effort:** Small | **File:** `ontologies/mi-provenance.ttl`

**Problem:** Q8 uses `?activity prov:generated ?canister` (forward property). The data asserts `?canister prov:wasGeneratedBy ?activity` (inverse). rdflib does not infer inverses. Result: Q8 returns 1 row with var2–var5 empty.

**Fix:**
1. Add `mi:CanisterSealingActivity prov:generated mi:LaughCanister_CAN20240315042 .` to `mi-provenance.ttl`
2. Cross-link provenance agent to seed comedian: add `mi:Agent_Sulley owl:sameAs <https://vocab.monstersinc.com/comedian/emp-001> .`
3. Optionally add forward `prov:generated` triples for all other activity→entity pairs in the file for consistency.

**Verification:** `make Q=Q8 query-one` must return a full chain with comedian, station, and door populated.

---

### 1.2 Stale Seed Data — Queries Q1, Q3, Q5, Q6 Return Zero Rows
**Priority:** P1-Critical | **Effort:** Medium | **Files:** `scripts/seed_data.py`, `data/scare_records.json`

**Problem:** All PerformanceRecords are dated 2021–2024-03-15. CDAIncidents are from 2023–2024. Queries filter on `NOW()` (2026-05-27). Result: Q1 (this month), Q3 (last 4 quarters), Q5 (next 30 days), Q6 (last 12 months) all return 0 rows.

**Fixes:**
1. In `seed_data.py`, replace loading of hardcoded performance dates from `scare_records.json` with dynamically computed dates relative to `date.today()`. Spread ~80 records across the last 13 months.
2. Add at least 3 `mi:CDAIncident` instances in `seed_data.py` dated within the last 12 months (distribute across quarters for Q3).
3. Add one `mi:TrainingRecord` with `expiresAt = date.today() + timedelta(days=14)` to trigger Q5.
4. Re-run `make seed` to regenerate `data/seed_graph.ttl`.

**Verification:** `make query` must show non-empty results for all 8 queries.

---

### 1.3 Process TTL Label Rotation (P2–P4)
**Priority:** P1-Critical | **Effort:** Small | **File:** `ontologies/mi-process.ttl`

**Problem:** TTL labels for P2–P4 are rotated one position. `mi:P2_*` models canister extraction (should be P3), `mi:P3_*` models comedian onboarding (should be P4), `mi:P4_*` models door maintenance (unlabelled in spec). Any SPARQL joining process labels to domain actors produces wrong results.

**Fix:**
1. Rename and relabel all three process instances to match spec:
   - `mi:P2_DoorDispatch` — Door Dispatch & Return — domains D3, D2 — trigger: `PortalActivationRequest`
   - `mi:P3_EnergyProcessing` — Energy Processing & Distribution — domain D1 — trigger: `CanisterFilledEvent`
   - `mi:P4_ComedianOnboarding` — Comedian Onboarding & Certification — domains D4, D2 — trigger: `NewHireEvent`

**Verification:** SPARQL `SELECT ?p ?label WHERE { ?p a mi:BusinessProcess ; rdfs:label ?label }` returns all 7 correctly labelled processes.

---

### 1.4 DoorContaminationShape Severity
**Priority:** P1-High | **Effort:** Trivial | **File:** `shapes/mi-compliance.shacl.ttl`

**Problem:** `DoorContaminationShape` uses `sh:Warning`. A quarantine failure after a 2319 incident is a CDA regulatory violation, not a warning.

**Fix:** Change `sh:severity sh:Warning` to `sh:severity sh:Violation` in `DoorContaminationShape`.

---

### 1.5 ChildProfile Blank Nodes (Q7 Cannot Match)
**Priority:** P2-High | **Effort:** Small | **Files:** `scripts/seed_data.py`, `data/seed_graph.ttl`

**Problem:** `mi:ChildProfile` instances are blank nodes in seed data. Q7 (detect profiles assigned to multiple doors) returns 0 rows because SPARQL cannot unify two blank nodes representing the same logical profile.

**Fix:** Mint URIs for all ChildProfile instances in `seed_data.py` using a deterministic scheme: `<https://vocab.monstersinc.com/profile/{portal_code}>`. Add 2–3 instances where the same profile URI is linked to multiple doors to make Q7 demonstrable.

---

### 1.6 CDAIncidentCompleteShape No-op Constraint
**Priority:** P3-Low | **Effort:** Trivial | **File:** `shapes/mi-compliance.shacl.ttl`

**Fix:** Change `sh:minCount 0` on `mi:involvedDoor` to `sh:minCount 1` with `sh:severity sh:Warning`, or remove the constraint. `sh:minCount 0` is the SHACL default and performs no validation.

---

## Phase 2 — Standards Violations

These are OWL/SHACL/SKOS conformance errors that produce unsound reasoning or non-portable behaviour.

### 2.1 OWL Restrictions Misused as Runtime Constraints
**Priority:** P1-Critical | **Effort:** Small | **File:** `ontologies/mi-core.ttl`

**Problem:** `owl:hasValue mi:active` on `mi:doorStatus` (lines ~117-120) and `owl:hasValue "true"^^xsd:boolean` on `mi:sealStatus` (lines ~133-137) are description-logic necessary conditions, not closed-world constraints. Under Open World Assumption a reasoner treats any door/canister as consistent unless it explicitly contradicts the value. These produce unsound inferences.

**Fix:** Remove the `owl:hasValue` restrictions from `mi:ChildDoor` and `mi:LaughCanister` class definitions. The constraints are already covered by SHACL shapes — no semantic loss.

---

### 2.2 Missing `owl:NamedIndividual` Declarations
**Priority:** P2-High | **Effort:** Small | **File:** `ontologies/mi-core.ttl`

**Problem:** `owl:oneOf` enumeration members (`mi:active`, `mi:quarantined`, `mi:maintenance`, `mi:decommissioned`, `mi:AMShift`, `mi:PMShift`, etc.) are declared with `a mi:DoorStatus` but not `a owl:NamedIndividual`. OWL 2 requires both for reasoner conformance.

**Fix:** Add `a owl:NamedIndividual` to all enumeration members in the ontology.

---

### 2.3 SKOS Hierarchy Error — ScreamEnergy
**Priority:** P2-High | **Effort:** Trivial | **File:** `ontologies/mi-glossary.ttl`

**Problem:** `mi:ScreamEnergy skos:broader mi:LaughEnergy` implies scream energy is a type of laugh energy — semantically backwards. They are sibling concepts.

**Fix:**
1. Introduce top concept `mi:EnergySource` with `skos:topConceptOf mi:MonsterIncGlossary`
2. Set both `mi:LaughEnergy skos:broader mi:EnergySource` and `mi:ScreamEnergy skos:broader mi:EnergySource`
3. Add `skos:historyNote` on `mi:ScreamEnergy`: "Deprecated as primary energy source following 2319 incident and transition to laugh-based operations."

---

### 2.4 OWL/SKOS URI Collision — Ambiguous Class/Concept Identity
**Priority:** P2-Medium | **Effort:** Small | **Files:** `ontologies/mi-core.ttl`, `ontologies/mi-glossary.ttl`

**Problem:** Several URIs are asserted as both `owl:Class` and `skos:Concept` (e.g. `mi:Comedian`, `mi:CDAIncident`, `mi:ChildProfile`). Technically permissible but confusing for reasoners and agents loading both graphs.

**Fix:** Add `skos:exactMatch` alignments in `mi-glossary.ttl` between the SKOS concepts and the OWL classes. Document the dual-use pattern in a comment.

---

### 2.5 SHACL CDAReportingShape — Invalid Duration Arithmetic
**Priority:** P2-High | **Effort:** Small | **File:** `shapes/mi-core.shacl.ttl`

**Problem:** `FILTER (?delay > "PT30M"^^xsd:duration)` where `?delay` is computed by subtracting two `xsd:dateTime` values — this is undefined in SPARQL 1.1. Works in rdflib as an extension but is not portable.

**Fix:** Replace with seconds-based arithmetic:
```sparql
BIND((?reportedAt - ?detectedAt) AS ?delaySeconds)
FILTER (?delaySeconds > 1800)
```
Note: rdflib returns duration differences as `xsd:decimal` seconds when two `xsd:dateTime` values are subtracted.

---

### 2.6 PerformanceRecordShape Severity Downgrade
**Priority:** P3-Medium | **Effort:** Trivial | **File:** `shapes/mi-core.shacl.ttl`

**Problem:** `mi:comedian` and `mi:date` constraints on `PerformanceRecordShape` use `sh:Warning`. These are operationally mandatory — a PerformanceRecord without a comedian or date is invalid data, not a warning.

**Fix:** Change `sh:severity sh:Warning` to `sh:severity sh:Violation` for both `mi:comedian` and `mi:date` property shapes.

---

### 2.7 Missing Disjointness Axioms
**Priority:** P3-Medium | **Effort:** Small | **File:** `ontologies/mi-core.ttl`

**Problem:** Only Comedian/DoorTechnician are declared disjoint. An agent can classify any instance as multiple entity types (e.g. a ChildDoor as a LaughCanister) without contradiction.

**Fix:** Add `owl:AllDisjointClasses` declaration covering all 12 core classes, or targeted `owl:disjointWith` for the highest-risk pairings: ChildDoor/LaughCanister, CDAIncident/PerformanceRecord, ChildProfile/TrainingRecord.

---

### 2.8 Duplicate SHACL Shape Consolidation
**Priority:** P3-Low | **Effort:** Small | **Files:** `shapes/mi-core.shacl.ttl`, `shapes/mi-compliance.shacl.ttl`

**Problem:** `CanisterTransportShape` (core) and `CanisterHandlingShape` (compliance) overlap significantly — both check sealStatus and fillLevel. Divergence risk over time.

**Fix:** Retain `CanisterTransportShape` as the authoritative constraint. In `CanisterHandlingShape`, replace duplicated property checks with a `sh:not sh:nodeShape` reference to the base shape, or document the deliberate scope difference (transit-only vs. all-stages).

---

## Phase 3 — Gaps (New Capabilities)

These address the stated downstream aim: AI agents that can reason over and act within the company's operations.

### 3.1 Agent-Grade Authority Ontology Module (Full)
**Priority:** P1-High Strategic | **Effort:** Large | **New file:** `ontologies/mi-agent-model.ttl`

**Rationale:** Without this, agents have no machine-readable answer to "am I authorised to do X?" or "when must I pause and wait for a human?" The SHACL constraints are excellent pre-condition checks but do not model authority or escalation.

**Contents to model:**

| Class / Property | Purpose |
|---|---|
| `mi:Policy` | Links a set of permissions to a scope (process, step, or entity type) |
| `mi:Permission` | `mi:action` (allow/deny), `mi:onEntity` (class), `mi:requiresRole` (Role) |
| `mi:AuthorityLevel` (xsd:integer 1–5) | Maps to `mi:clearanceLevel` on DoorTechnician; gates dispatch authority |
| `mi:HITLTrigger` | `mi:triggerCondition` (SPARQL expression), `mi:escalatesTo` (Role), `mi:escalationDeadline` (xsd:duration) |
| `mi:DataClassification` | Enumeration: Public, Internal, Restricted, SensitivePersonalData |
| `mi:automatable` (xsd:boolean) | On each `mi:ProcessStep` — distinguishes human vs. agent-executable steps |

**Key assertions to make:**
- `mi:ChildProfile mi:dataClassification mi:SensitivePersonalData`
- `mi:employeeId mi:dataClassification mi:Internal`
- `mi:HITLTrigger` instances for: (a) 2319 contamination alert → escalate to CDA Liaison Officer within PT30M, (b) laugh score below threshold for 3+ sessions → escalate to Floor Manager, (c) CDA incident severity ≥ 4 → escalate to CCO Mike Wazowski
- `mi:automatable true` on dispatcher, scan, and logging steps; `mi:automatable false` on comedy performance, supervisor intervention, CDA contact

**New document:** `docs/13-agent-model.md` — View: Agent Orchestration | Standard: OWL 2 + custom authority ontology

---

### 3.2 People & Culture — Org Hierarchy + Domain Ownership
**Priority:** P2-High | **Effort:** Medium | **Files:** `ontologies/mi-core.ttl`, `data/seed_graph.ttl`

**Schema additions (`mi-core.ttl`):**
- `mi:reportsTo` — FunctionalProperty, domain/range `mi:Monster`
- `mi:manages` — inverse of `mi:reportsTo`
- `mi:holdsTitleRole` — ObjectProperty linking Monster to named Role individual
- `mi:domainOwner` — ObjectProperty: `mi:Domain` → `mi:Monster`
- Named Role individuals: `mi:CEO`, `mi:CCO`, `mi:CDADirector`, `mi:FloorManager`, `mi:VPLogistics`, `mi:VPEnergy`, `mi:ChiefPeopleOfficer`, `mi:RDDirector`

**Seed assertions (`seed_graph.ttl` via `seed_data.py`):**
```turtle
mi:emp-001 mi:holdsTitleRole mi:CEO ; mi:manages mi:emp-002, mi:emp-003 .
mi:emp-002 mi:holdsTitleRole mi:CCO ; mi:reportsTo mi:emp-001 .
mi:emp-003 mi:holdsTitleRole mi:CDADirector ; mi:reportsTo mi:emp-001 .
mi:LaughOperations mi:domainOwner mi:emp-002 .
mi:RDLaughter mi:domainOwner mi:emp-002 .
mi:CDACompliance mi:domainOwner mi:emp-003 .
```
(Complete all 6 domain ownership assertions and full reporting hierarchy.)

**Verification:** SPARQL `SELECT ?monster ?role WHERE { ?monster mi:holdsTitleRole ?role }` returns all named leaders.

---

### 3.3 CDA Incident Lifecycle — Audit Completeness
**Priority:** P2-High | **Effort:** Medium | **Files:** `ontologies/mi-core.ttl`, `shapes/mi-compliance.shacl.ttl`

**Problem:** An incident can remain permanently open with no resolution timestamp and no way to navigate to its regulatory submission.

**Additions:**
1. `mi:incidentStatus` — ObjectProperty pointing to `mi:IncidentStatus` individuals: `mi:Open`, `mi:Contained`, `mi:Escalated`, `mi:Closed`, `mi:SubmittedToRegulator`
2. `mi:CDAComplianceReport` class with: `mi:submittedAt` (xsd:dateTime), `mi:cdaAcknowledgedAt` (xsd:dateTime), `mi:filedBy` (mi:Monster), `mi:coversIncident` (mi:CDAIncident)
3. `mi:reportedIn` — ObjectProperty: `mi:CDAIncident` → `mi:CDAComplianceReport`
4. `prov:wasAttributedTo` assertion on each CDAIncident seed instance pointing to the responsible officer
5. New SHACL shape `CDAIncidentLifecycleShape`: require `mi:resolvedAt` when `mi:incidentStatus = mi:Closed`

---

### 3.4 Expand P2–P7 Process Stubs (All Remaining Processes)
**Priority:** P2-High | **Effort:** Large | **File:** `ontologies/mi-process.ttl`

After fixing labels (Phase 1.3), expand each stub to include:
- `mi:hasStep` individuals with `mi:stepOrder`, `mi:performedBy` (domain), `mi:produces`, `mi:consumes`
- `mi:triggeredBy` event assertion
- At least one `mi:hasException` step per process

**P5 (2319 CDA Incident Response)** gets the most detail given compliance priority:
- Steps: Contamination detected → Station sealed → Comedian isolated → CDA API notified → Decontamination team dispatched → Scene cleared → CDA report filed → Incident closed
- Exception: CDA escalation if severity ≥ 4 → CCO notification
- Produces: `mi:CDAIncident`, `mi:CDAComplianceReport`
- SLA: Must complete within PT30M

**P2 (Door Dispatch & Return):**
- Steps: Dispatch request → Vault retrieval → Quality check → Portal activation → Session run → Portal deactivation → Return to vault → Maintenance scheduling
- Exception: Quality check fail → Quarantine → Replacement request

**P3 (Energy Processing & Distribution):**
- Steps: Canister intake → Barcode scan → Extraction → EnergyUnit creation → Grid dispatch → Ledger reconciliation → Grid authority acknowledgement

**P4 (Comedian Onboarding & Certification):**
- Steps: Hire event → Welcome + briefing → Safety training → Technique training → Certification exam → Cert level assignment → Station assignment
- Exception: Exam fail → Remedial training loop (max 3 attempts)

**P6, P7:** Minimum viable stubs (trigger, 4 steps, output, exception).

---

### 3.5 DCAT Catalog Completeness
**Priority:** P2-Medium | **Effort:** Small | **File:** `ontologies/mi-catalog.ttl`

**Additions:**
1. Add `dcat:distribution` to the 6 datasets that currently lack it: `mi:CDAIncidentLog`, `mi:TrainingRegistry`, `mi:ChildProfiles`, `mi:RDPrototypes`, `mi:CDAComplianceReports`, `mi:EnergyGridForecast`
2. Add missing 5 datasets to `mi:SPARQLEndpoint dcat:servesDataset`
3. Add `dct:accessRights` and `mi:dataClassification mi:SensitivePersonalData` annotations to `mi:ChildProfiles`
4. Add `dct:temporal` retention bound to `mi:ChildProfiles` and `mi:CDAIncidentLog`
5. Fix hardcoded `dct:modified "2024-03-15"` on catalog — update to current date or make dynamic

---

### 3.6 R2RML Structural Alignment
**Priority:** P3-Medium | **Effort:** Medium | **File:** `mappings/mi-db.r2rml.ttl`

**Fixes:**
1. Restructure `CHILD_DOOR` map to emit a `mi:ChildProfile` intermediate node via blank-node term map, matching the seed graph shape
2. Add `CHILD_DOOR.door_status` → `mi:doorStatus` column mapping (currently absent)
3. Add `COMEDIAN.station_id` → `mi:assignedStation` join map (not just the string `mi:stationId`)
4. Add table maps for `TRAINING_RECORD` and `CDA_INCIDENT` tables
5. Replace MySQL-specific `DATEDIFF(CURDATE(), ...)` with standard SQL in `DoorMaintenanceView`

---

### 3.7 Compliance Query Gap Fill
**Priority:** P3-Medium | **Effort:** Small | **File:** `queries/compliance-violations.sparql`

**Add:**
- CV4: Mirror `DoorContaminationShape` — doors in `quarantined` status with no CDA incident reference
- CV5: Mirror `CanisterHandlingShape` — canisters with `fillLevel > 0` but `sealStatus = false`
- CV6: Mirror `ChildAgeShape` — doors dispatched to profiles with `ageRange` starting "13"
- CV7: Open CDA incidents (no `mi:resolvedAt` or status ≠ Closed) older than 30 days

---

### 3.8 SPARQL Variable Aliases
**Priority:** P3-Low | **Effort:** Small | **File:** `queries/business-questions.sparql`

**Problem:** All SELECT expression results display as `var0`, `var1` etc. in SPARQL clients reporting positional bindings.

**Fix:** Add `AS ?alias` to all bare expressions. Key ones:
- Q2: `AS ?portalCode`, `AS ?lastMaintained`, `AS ?daysOverdue`
- Q3: `AS ?year`, `AS ?quarter`, `AS ?incidentCount`
- Q4: `AS ?certLevel`, `AS ?avgConversionRate`
- Q6: `AS ?year`, `AS ?month`, `AS ?totalMWh`

---

### 3.9 Documentation Additions
**Priority:** P3-Medium | **Effort:** Medium

**`docs/00-overview.md`:**
- Add org-chart PlantUML diagram (hierarchy: CEO → CCO / VP team → domain leads)
- Add "Why this matters" explicit section
- Add one SPARQL snippet (e.g. domain ownership query)

**`docs/02-capability-map.md`:**
- Add SPARQL artifact showing capability-to-domain query

**`docs/07-service-catalog.md`:**
- Add Turtle snippet showing one ArchiMate-annotated service in RDF

**`docs/13-agent-model.md`** (new — from 3.1):
- Full view of the agent-grade authority ontology

**Culture stub in `docs/00-overview.md` or new `docs/14-culture.md`:**
- SKOS fragment with Monsters Inc. cultural values (Collaboration, Psychological Safety, Joy-Based Performance)
- `mi:EraTransition` PROV-O event with before/after metric snapshots (attrition, yield)

---

## Summary Scorecard

| Phase | Items | Est. Files Changed |
|-------|-------|--------------------|
| Phase 1 — Bugs | 6 items | ontologies/mi-provenance.ttl, scripts/seed_data.py, ontologies/mi-process.ttl, shapes/mi-compliance.shacl.ttl |
| Phase 2 — Standards | 8 items | ontologies/mi-core.ttl, ontologies/mi-glossary.ttl, shapes/mi-core.shacl.ttl, shapes/mi-compliance.shacl.ttl |
| Phase 3 — Gaps | 9 items | +1 new ontology (mi-agent-model.ttl), +1 new doc (13-agent-model.md), extensions to seed_data.py, mi-catalog.ttl, mi-process.ttl, mi-db.r2rml.ttl, queries/*.sparql |

**Confidence that `make all` passes after Phase 1:** Very high  
**Confidence that Q1–Q8 all return results after Phase 1+2:** High (Q7 depends on Phase 1.5)  
**Agent-grade consumption readiness after all 3 phases:** Significantly improved — authority model + HITL triggers + data classification make this ontology consumable by autonomous agents as designed
