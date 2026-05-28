# Monsters, Inc. — Enterprise Overview

> **View:** High-Level Architecture | **Standard:** ArchiMate 3 (PlantUML approximation) | **Audience:** All stakeholders

This document provides the entry point to the Monsters, Inc. enterprise architecture. It establishes the company in its operating context, maps the six enterprise pillars, and introduces the six domains that all subsequent views elaborate.

**Navigation:** [Spec](../.claude/prompts/spec.md) | [Domain Model →](01-domain-model.md) | [Capability Map →](02-capability-map.md) | [All Views →](../README.md)

---

## 1. Enterprise Context

Monsters, Inc. operates at the intersection of two worlds — Monstropolis and the Human World — mediated by a proprietary portal network of 10+ million child bedroom doors. Energy is the product; laughter is now the source.

<!-- diagram-image -->
![Monsters, Inc. — Enterprise Context Diagram — (ArchiMate: System Context View)](../images/diagrams/00-overview__1__MI-Enterprise-Context.png)

```plantuml
@startuml MI-Enterprise-Context
!theme plain
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Helvetica
skinparam rectangleBorderColor #555555
skinparam rectangleBackgroundColor #F8F8F8
skinparam rectangleFontSize 12
skinparam arrowColor #444444
skinparam arrowFontSize 10
skinparam noteBorderColor #AAAAAA
skinparam noteBackgroundColor #FFFDE7

title Monsters, Inc. — Enterprise Context Diagram\n(ArchiMate: System Context View)

' ─── External actors ───────────────────────────────────
rectangle "Human World\n(Parallel Dimension)" as HW #FDEBD0 {
  agent "Human Children\n(Energy Sources)" as HC
}

rectangle "Child Detection Agency\n(CDA)" as CDA #FDEDEC {
  agent "CDA Officers\n& Inspectors" as CDAO
}

rectangle "Monstropolis\nPower Grid Authority" as MPGA #EAF2FB {
  agent "Grid Control\nCentre" as GCC
}

rectangle "Monsters University" as MU #EAF7F4 {
  agent "Comedian\nGraduates" as CG
}

' ─── Monsters, Inc. enterprise boundary ────────────────
rectangle "**Monsters, Inc.**\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" as MI #EBF5FB {

  rectangle "D1  Energy Production" as D1 #D6EAF8
  rectangle "D2  Laugh Operations" as D2 #D5F5E3
  rectangle "D3  Door Management & Logistics" as D3 #FDFEFE
  rectangle "D4  HR & Training" as D4 #F5EEF8
  rectangle "D5  CDA Compliance & Safety" as D5 #FDEBD0
  rectangle "D6  R&D — Laughter Initiative" as D6 #E8F8F5

}

' ─── External relationships ────────────────────────────
HC  --> D2 : Laugh energy\n(via bedroom doors)
D3  --> HC : Portal access\n(door dispatch)
CDA --> D5 : Regulatory mandates\n& incident authority
D5  --> CDA : Incident reports\n& audit submissions
D1  --> MPGA : Processed energy\n(MWh, real-time)
MPGA --> D1 : Capacity forecasts\n& demand signals
MU  --> D4 : Qualified comedians\n(recruitment pipeline)
D4  --> MU : Industry placement\n& sponsored research

' ─── Internal relationships ────────────────────────────
D3 ..> D2 : Door dispatch\n& return
D4 ..> D2 : Certified comedians\n& floor managers
D2 ..> D1 : Laugh canisters\n(raw energy)
D5 ..> D2 : Safety clearance\n& incident response
D6 ..> D2 : New techniques\n& prototypes
D1 ..> D6 : R&D funding\n(revenue share)

@enduml
```

---

## 2. Six Enterprise Pillars

The Open Group's six enterprise strategy pillars map cleanly to Monsters, Inc.'s current operating reality. The company's transformation from fear-based to laughter-based energy is visible in every pillar.

<!-- diagram-image -->
![Monsters, Inc. — Six Enterprise Pillars — (ArchiMate: Motivation View)](../images/diagrams/00-overview__2__MI-Six-Pillars.png)

```plantuml
@startuml MI-Six-Pillars
!theme plain
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Helvetica
skinparam rectangleBorderColor #888888
skinparam rectangleFontSize 11
skinparam noteFontSize 10
skinparam arrowColor #666666

title Monsters, Inc. — Six Enterprise Pillars\n(ArchiMate: Motivation View)

' ─── Pillars ───────────────────────────────────────────
rectangle "STRATEGY\n──────────────────\nPivot from fear → laughter\nenergy. Dominate clean\nenergy market. Ethical\nsourcing mandate.\n \nGoal: 100 MWh/shift\nby FY28" as STR #FFFDE7

rectangle "METHODS\n──────────────────\nLaughter collection protocol\n(LCP-v3). Door portal ops.\nEnergy processing SOP.\nCDA compliance playbook.\n \nOwned by: Operations" as MTH #E8F5E9

rectangle "PEOPLE\n──────────────────\n1,200 monsters; 8 role\ntypes. Career ladder:\nTrainee → Comedian →\nSenior → Floor Manager.\n \nAttrition target: < 5%" as PPL #F3E5F5

rectangle "CULTURE\n──────────────────\nFrom: fear-based competition\nTo: joy-based collaboration\nPsychological safety is an\noperational requirement.\n \nMetric: Comedy NPS" as CLT #FFF3E0

rectangle "TECHNOLOGY\n──────────────────\n10M+ door portal network.\nLaugh Floor Mgmt System.\nEnergy containment grid.\nCDA Integration API.\nTraining simulators." as TCH #E3F2FD

rectangle "OPERATIONS\n──────────────────\n2 shifts/day, 100 stations.\nDoor logistics pipeline.\n24/7 energy processing.\nReal-time CDA monitoring.\nQuarterly R&D trials." as OPS #FCE4EC

' ─── Linkages ──────────────────────────────────────────
STR --> MTH : drives
STR --> PPL : requires
MTH --> OPS : operationalises
PPL --> CLT : shapes
CLT --> MTH : transforms
TCH --> OPS : enables
OPS --> STR : measures against

note right of STR
  **Domains served**
  All six domains
  underpin strategy
  execution
end note

note right of OPS
  **Primary domains:**
  D1 · D2 · D3
end note

note right of PPL
  **Primary domain:**
  D4 (HR & Training)
end note

note right of TCH
  **Primary domains:**
  D3 · D2 · D1
end note

@enduml
```

---

## 3. Domain Landscape

The six domains and their primary inter-domain data and process flows. This is the **bounded context map** — the starting point for all subsequent domain and capability modeling.

<!-- diagram-image -->
![Monsters, Inc. — Domain Landscape — (Bounded Context Map)](../images/diagrams/00-overview__3__MI-Domain-Landscape.png)

```plantuml
@startuml MI-Domain-Landscape
!theme plain
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Helvetica
skinparam packageBorderColor #666666
skinparam packageBackgroundColor #FAFAFA
skinparam componentBorderColor #888888
skinparam componentFontSize 11
skinparam arrowColor #444444
skinparam arrowFontSize 9
skinparam arrowThickness 1.5

title Monsters, Inc. — Domain Landscape\n(Bounded Context Map)

' ─── Domain packages ───────────────────────────────────
package "D1 · Energy Production" as D1 #D6EAF8 {
  [Energy Processing\nPlant] as EPP
  [Grid Distribution\nController] as GDC
  [Canister Intake\nStation] as CIS
}

package "D2 · Laugh Operations" as D2 #D5F5E3 {
  [Laugh Floor\nManagement] as LFM
  [Shift Scheduling\nEngine] as SSE
  [Performance\nTracker] as PFT
}

package "D3 · Door Management\n& Logistics" as D3 #EAF7F4 {
  [Door Vault\nSystem (10M+)] as DVS
  [Portal Network\nController] as PNC
  [Maintenance\nScheduler] as MTS
}

package "D4 · HR & Training" as D4 #F5EEF8 {
  [Monster\nRegistry] as MRG
  [Certification\nEngine] as CRE
  [Performance\nReview System] as PRS
}

package "D5 · CDA Compliance\n& Safety" as D5 #FDEBD0 {
  [Incident\nManagement] as IMS
  [Audit & Report\nGenerator] as ARG
  [Decontamination\nProtocol Engine] as DPE
}

package "D6 · R&D — Laughter\nInitiative" as D6 #E8F8F5 {
  [Technique\nResearch Lab] as TRL
  [Prototype\nTest Platform] as PTP
  [IP & Patent\nRegistry] as IPR
}

' ─── Core operational flows ────────────────────────────
D3 --> D2 : <<door dispatch>>\nPortalActivationEvent
D2 --> D1 : <<canister transfer>>\nFilledLaughCanister
D4 --> D2 : <<staffing>>\nCertifiedComedian
D6 --> D2 : <<technique rollout>>\nNewComedyProtocol
D2 --> D4 : <<performance data>>\nPerformanceRecord
D5 --> D2 : <<clearance / halt>>\nComplianceDecision
D5 --> D3 : <<door flag / destroy>>\nDoorStatusUpdate
D1 --> D6 : <<R&D funding>>\nRevenueAllocation
D6 --> D1 : <<yield data>>\nPrototypeEnergyResult

' ─── Annotations ───────────────────────────────────────
note top of D2
  **Core value-creating domain**
  All other domains either
  feed into or depend on
  Laugh Operations
end note

note bottom of D5
  **Cross-cutting concern**
  CDA compliance touches
  D1, D2, D3 simultaneously
end note

@enduml
```

---

## 4. Modeling Views Map

This project produces sixteen interconnected modeling views. The table below shows which standard each view uses and which domain(s) it covers.

<!-- diagram-image -->
![Monsters, Inc. — Artifact & View Map — (How the 16 documents relate to each other)](../images/diagrams/00-overview__4__MI-Views-Map.png)

```plantuml
@startuml MI-Views-Map
!theme plain
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Helvetica
skinparam rectangleBorderColor #AAAAAA
skinparam rectangleBackgroundColor #F9F9F9
skinparam rectangleFontSize 10
skinparam arrowColor #777777
skinparam arrowFontSize 9

title Monsters, Inc. — Artifact & View Map\n(How the 16 documents relate to each other)

left to right direction

rectangle "00 Overview\n(this doc)" as V00 #E3F2FD
rectangle "01 Domain Model\n(OWL classes)" as V01 #D5F5E3
rectangle "02 Capability Map\n(ArchiMate)" as V02 #D5F5E3
rectangle "03 Business Process\n(BPMN-style)" as V03 #FFF9C4
rectangle "04 Ontology BPM\n(OBPM)" as V04 #FFF9C4
rectangle "05 Data Catalog\n(DCAT 3)" as V05 #FCE4EC
rectangle "06 Data Lineage\n(PROV-O)" as V06 #FCE4EC
rectangle "07 Service Catalog\n(ArchiMate)" as V07 #EDE7F6
rectangle "08 Glossary\n(SKOS)" as V08 #FFF3E0
rectangle "09 Constraints\n(SHACL + SPARQL)" as V09 #FFCCBC
rectangle "10 Entity Graph\n(OWL + UML)" as V10 #E8F5E9
rectangle "11 DB Schema\n(R2RML + SQL)" as V11 #E0F2F1
rectangle "12 Unstructured Docs\n(Doc Ontology)" as V12 #F3E5F5
rectangle "13 Agent Authority\n(OWL + SHACL)" as V13 #FFE0B2
rectangle "14 Data Governance\n(ODRL + SHACL)" as V14 #FFE0B2
rectangle "15 Constitution\n(OWL + SKOS)" as V15 #FFE0B2

V00 --> V01 : domain\nentities
V00 --> V02 : capabilities
V01 --> V03 : entities\nin process
V01 --> V04 : OWL\nannotation
V03 --> V04 : process\nsteps
V01 --> V10 : class\nhierarchy
V10 --> V09 : shape\ntargets
V10 --> V11 : table\nmapping
V01 --> V05 : dataset\ndefinitions
V06 --> V05 : lineage\nrecords
V08 --> V01 : term\ndefinitions
V07 --> V02 : service\ndecomposition
V12 --> V05 : doc\nresources
V09 --> V06 : violation\nlineage
V13 --> V03 : permitted\nsteps
V13 --> V09 : authority\nshapes
V14 --> V07 : service\naccess
V14 --> V13 : agent\nidentity
V15 --> V13 : enforced\nprinciples
V15 --> V09 : compliance\nbindings

@enduml
```

---

## 5. Energy Production Snapshot

A quick illustration of the core value chain — from child laughter through to Monstropolis city power.

<!-- diagram-image -->
![Monsters, Inc. — Core Value Chain — (Energy Production Flow)](../images/diagrams/00-overview__5__MI-Value-Chain.png)

```plantuml
@startuml MI-Value-Chain
!theme plain
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Helvetica
skinparam activityBorderColor #666666
skinparam activityBackgroundColor #F0F0F0
skinparam activityArrowColor #444444
skinparam activityFontSize 11
skinparam noteBackgroundColor #FFFDE7

title Monsters, Inc. — Core Value Chain\n(Energy Production Flow)

|#D5F5E3| Laugh Operations (D2)|
start
:Comedian enters child's room\nvia Door Portal;
note right
  Triggered by:
  ShiftStartEvent
end note
:Child laughs;
:Laugh energy captured\nin LaughCanister;
:Canister sealed & logged\n(CanisterFilledEvent);

|#D6EAF8| Energy Production (D1)|
:Canister received at\nIntake Station;
:Energy extraction process\n(~14.5 MWh/canister avg);
:Raw energy converted\nto electrical units;
:Units registered in\nEnergyLedger;
:Energy dispatched to\nMonstropolis Grid;

|#EAF7F4| Door Management (D3)|
:Door de-activated &\nreturned to vault;
:Door status updated\nin PortalNetworkController;
:Next maintenance date\nscheduled;

|#FDEBD0| CDA Compliance (D5)|
:Shift closure audit\n(automated);
if (Any incidents?) then (yes)
  :Trigger 2319 Protocol;
  :CDA notification sent;
else (no)
  :Compliance log entry;
endif

stop

@enduml
```

---

## 6. What's Next

| Document | What it adds |
|----------|-------------|
| [01 — Domain Model](01-domain-model.md) | Full OWL class hierarchy; domain ontology in Turtle |
| [02 — Capability Map](02-capability-map.md) | ArchiMate capability heat-map; strategic alignment |
| [03 — Business Process](03-business-process.md) | Complete Daily Laugh Run process (BPMN-style) |
| [04 — Ontology BPM](04-ontology-bpm.md) | Same process annotated with OWL — the OBPM view |
| [05 — Data Catalog](05-data-catalog.md) | DCAT 3 catalog of all 12 Monsters, Inc. data assets |
| [06 — Data Lineage](06-data-lineage.md) | PROV-O lineage chain from laugh to Monstropolis grid |
| [07 — Service Catalog](07-service-catalog.md) | ArchiMate application & technology service map |
| [08 — Glossary](08-glossary.md) | SKOS concept scheme — 40+ defined terms |
| [09 — Constraints & Queries](09-constraints-queries.md) | SHACL shapes + SPARQL business queries |
| [10 — Entity Graph](10-entity-graph.md) | Full OWL entity-relationship + RDF graph view |
| [11 — DB Schema](11-db-schema.md) | SQL schema + R2RML relational→RDF mapping |
| [12 — Unstructured Docs](12-unstructured-docs.md) | CDA forms & incident reports as typed RDF resources |
| [13 — Agent Authority & Orchestration](13-agent-model.md) | Which actions an autonomous agent may take, how authority resolves, and when it must escalate to a human |
| [14 — Data Governance, Identity & Access](14-data-governance.md) | Who may reach which systems and data, under which W3C ODRL policies — the layer the agent consults before any read |
| [15 — Constitution & Defensibility](15-constitution.md) | Company principles & regulatory requirements linked to the exact SHACL/SPARQL that enforces them |

---

## Schema Anchor

Every view in this overview ultimately resolves against one shared OWL schema — the core ontology whose header is reproduced below. Its single URI base (`https://vocab.monstersinc.com/ontology#`) is what lets sixteen otherwise-independent documents reference the same `mi:` terms without drift.

<!-- excerpt-from: ontologies/mi-core.ttl -->
```turtle
@prefix mi:    <https://vocab.monstersinc.com/ontology#> .
<https://vocab.monstersinc.com/ontology>
    a owl:Ontology ;
    rdfs:label "Monsters, Inc. Core Ontology" ;
```

---

## Why this matters

A single navigable overview is what turns sixteen separate standards artifacts into one coherent, traversable model rather than a pile of disconnected files. The Views Map makes the dependencies between views explicit, so a reader — or an autonomous agent — can follow any concept from its glossary definition through its OWL class, its process, its data catalog entry, and the SHACL shapes that govern it. Without this entry point, the cross-references that make the model defensible would be invisible, and consumers like MS IQ would have no starting node from which to walk the graph. The overview is, in effect, the table of contents that proves the architecture is integrated rather than merely co-located.
