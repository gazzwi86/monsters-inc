# Data Lineage — PROV-O Provenance Chain

> **View:** Lineage / Provenance | **Standard:** PROV-O (W3C) | **Audience:** Data Stewards, Compliance, Architects

This document traces the complete end-to-end data lineage for a single unit of clean energy — from the moment a child's laughter is captured at a Laugh Floor station, through canister sealing and energy extraction, to final dispatch to the Monstropolis Power Grid. By encoding this chain in PROV-O, Monsters, Inc. can audit any energy unit back to the comedian, the child door, and the exact shift that generated it.

> **Run it:** `make Q=Q8 query-one` — expected output: lineage chain showing Sulley → CAN-20240315-042 → EU-001 → Monstropolis Grid Zone A

**Navigation:** [← 05 Data Catalog](05-data-catalog.md) | [→ 07 Service Catalog](07-service-catalog.md) | [All Views →](../README.md)

---

## PROV-O Conceptual Overview

PROV-O (the W3C Provenance Ontology) models provenance using three core concepts:

| Concept | Description | Example in this chain |
|---------|-------------|----------------------|
| `prov:Entity` | A physical, digital, or conceptual thing | ChildLaugh, LaughCanister, EnergyUnit |
| `prov:Activity` | Something that occurred over a period of time | LaughCollectionActivity, CanisterSealing |
| `prov:Agent` | Something that bears responsibility for an activity | Sulley, Energy Processing Plant |

The key relationships between them are:

| Predicate | Direction | Meaning |
|-----------|-----------|---------|
| `prov:wasGeneratedBy` | Entity → Activity | This entity was produced by that activity |
| `prov:wasDerivedFrom` | Entity → Entity | This entity is derived from that entity |
| `prov:wasAssociatedWith` | Activity → Agent | This activity was performed by/under that agent |
| `prov:used` | Activity → Entity | This activity consumed or made use of that entity |
| `prov:wasInformedBy` | Activity → Activity | This activity was triggered/enabled by that activity |

---

## Diagram 1: PROV-O Lineage Graph

```plantuml
@startuml PROV-O-Lineage
!theme plain
skinparam backgroundColor #FFFFFF
skinparam objectBackgroundColor #fffde7
skinparam objectBorderColor #b0a000
skinparam arrowColor #555555
skinparam defaultFontSize 11

title PROV-O Lineage — EnergyUnit EU-20240315-042-001

' ── Entities (yellow) ──────────────────────────────────────────
object "ChildLaugh\n(prov:Entity)" as cl #fffde7
object "LaughFloorStation 042\n(mi:LaughFloorStation, prov:Entity)" as stn #fffde7
object "ChildDoor NYC-4821\n(mi:ChildDoor, prov:Entity)" as door #fffde7
object "LaughCanister CAN-20240315-042\n(mi:LaughCanister, prov:Entity)\nfillLevel=1.0 | capacity=14.5 MWh" as can #fffde7
object "EnergyUnit EU-20240315-042-001\n(mi:EnergyUnit, prov:Entity)\n14.5 MWh | Zone-A" as eu #fffde7

' ── Activities (light blue) ─────────────────────────────────────
object "DoorManufacturingActivity\n(prov:Activity)" as dma #e3f2fd
object "ShiftStartActivity\n(prov:Activity)\n08:00–09:00Z" as ssa #e3f2fd
object "LaughCollectionActivity\n(prov:Activity)\n09:00–09:47Z" as lca #e3f2fd
object "CanisterSealingActivity\n(prov:Activity)\n09:47–09:48:30Z" as csa #e3f2fd
object "EnergyExtractionActivity\n(prov:Activity)\n10:15–10:22Z" as eea #e3f2fd
object "GridDispatchActivity\n(prov:Activity)\n10:25–10:26Z" as gda #e3f2fd

' ── Agents (light green) ────────────────────────────────────────
object "Sulley\n(prov:Agent, mi:Comedian)\nEMP-001 | certLevel 5" as sulley #e8f5e9
object "Door Vault\n(prov:Agent)" as vault #e8f5e9
object "Energy Processing Plant\n(prov:Agent)" as plant #e8f5e9
object "Monstropolis Grid Authority\n(prov:Agent)" as grid #e8f5e9

' ── Edges ────────────────────────────────────────────────────────
door    <-- dma    : wasGeneratedBy
dma     --> vault  : wasAssociatedWith

cl      <-- lca    : wasGeneratedBy
lca     --> sulley : wasAssociatedWith
lca     --> stn    : used
lca     --> door   : used
lca     <-- ssa    : wasInformedBy

can     --> cl     : wasDerivedFrom
can     <-- csa    : wasGeneratedBy
csa     --> sulley : wasAssociatedWith

eu      --> can    : wasDerivedFrom
eu      <-- eea    : wasGeneratedBy
eea     --> can    : used
eea     --> plant  : wasAssociatedWith

gda     --> eu     : used
gda     --> grid   : wasAssociatedWith

@enduml
```

---

## Diagram 2: Temporal Swimlane

```plantuml
@startuml Temporal-Swimlane
!theme plain
skinparam backgroundColor #FFFFFF
skinparam swimlaneBorderColor #888888
skinparam activityBackgroundColor #e3f2fd
skinparam activityBorderColor #1565c0
skinparam defaultFontSize 11

title Laugh-to-Grid Temporal Flow — 2024-03-15

|Laugh Floor (Sulley)|
start
:**08:00Z** — Shift Start;
note right: ShiftStartActivity\ninforms collection
:**09:00Z** — Begin laugh collection\nStation 042 + Door NYC-4821;
:Sulley performs comedy routine;
:Child laughter captured → ChildLaugh entity;
:**09:47Z** — Collection complete\n(47 min session);
:Seal canister CAN-20240315-042\nfillLevel 1.0 | 14.5 MWh;
:**09:48:30Z** — Canister sealed\nand ready for transport;

|Energy Station (Processing Plant)|
:Canister received for extraction;
:**10:15Z** — Begin energy extraction;
:Laugh energy converted to electrical MWh;
:EnergyUnit EU-20240315-042-001 created\n14.5 MWh | Zone-A;
:**10:22Z** — Extraction complete;

|Grid (Monstropolis Grid Authority)|
:Energy unit prepared for dispatch;
:**10:25Z** — Grid dispatch begins;
:EU-20240315-042-001 transmitted\nto Monstropolis Grid Zone A;
:**10:26Z** — Dispatch confirmed;
:Provenance bundle recorded;
stop

@enduml
```

---

## PROV-O Relationships Table

All PROV-O triples modelled in `ontologies/mi-provenance.ttl`:

| Subject | Predicate | Object |
|---------|-----------|--------|
| `mi:ChildLaugh_20240315_042` | `prov:wasGeneratedBy` | `mi:LaughCollectionActivity` |
| `mi:LaughCollectionActivity` | `prov:wasAssociatedWith` | `mi:Agent_Sulley` |
| `mi:LaughCollectionActivity` | `prov:used` | `mi:LaughFloorStation_042` |
| `mi:LaughCollectionActivity` | `prov:used` | `mi:ChildDoor_NYC4821` |
| `mi:LaughCollectionActivity` | `prov:wasInformedBy` | `mi:ShiftStartActivity` |
| `mi:ChildDoor_NYC4821` | `prov:wasGeneratedBy` | `mi:DoorManufacturingActivity` |
| `mi:DoorManufacturingActivity` | `prov:wasAssociatedWith` | `mi:Agent_DoorVault` |
| `mi:LaughCanister_CAN20240315042` | `prov:wasDerivedFrom` | `mi:ChildLaugh_20240315_042` |
| `mi:LaughCanister_CAN20240315042` | `prov:wasGeneratedBy` | `mi:CanisterSealingActivity` |
| `mi:CanisterSealingActivity` | `prov:wasAssociatedWith` | `mi:Agent_Sulley` |
| `mi:EnergyExtractionActivity` | `prov:used` | `mi:LaughCanister_CAN20240315042` |
| `mi:EnergyExtractionActivity` | `prov:wasAssociatedWith` | `mi:Agent_EnergyProcessingPlant` |
| `mi:EnergyUnit_EU20240315042001` | `prov:wasDerivedFrom` | `mi:LaughCanister_CAN20240315042` |
| `mi:EnergyUnit_EU20240315042001` | `prov:wasGeneratedBy` | `mi:EnergyExtractionActivity` |
| `mi:GridDispatchActivity` | `prov:used` | `mi:EnergyUnit_EU20240315042001` |
| `mi:GridDispatchActivity` | `prov:wasAssociatedWith` | `mi:Agent_MonstropolisGrid` |
| `mi:EnergyLineageBundle` | `prov:wasGeneratedBy` | `mi:GridDispatchActivity` |

---

## Full Turtle Listing — mi-provenance.ttl

The complete PROV-O instance graph — agents, entities, activities, and the bundle wrapping the laugh → canister → energy → grid chain — is maintained in the source file. A representative excerpt (the terminal `EnergyUnit` entity with its derivation and generation links) appears below.

<!-- excerpt-from: ontologies/mi-provenance.ttl -->
```turtle
mi:EnergyUnit_EU20240315042001 a mi:EnergyUnit, prov:Entity ;
    rdfs:label "Energy Unit EU-20240315-042-001" ;
    mi:megawattHours "14.5"^^xsd:decimal ;
    mi:generatedAt   "2024-03-15T10:22:00Z"^^xsd:dateTime ;
    mi:gridZone      "Zone-A" ;
    prov:wasDerivedFrom mi:LaughCanister_CAN20240315042 ;
    prov:wasGeneratedBy mi:EnergyExtractionActivity .
```

> **Full artifact:** [ontologies/mi-provenance.ttl](../ontologies/mi-provenance.ttl) — generated/maintained as the single source of truth.

---

## Why This Matters

PROV-O provenance is what transforms raw energy data into auditable, regulatorily defensible records — if a CDA compliance officer queries which comedian operated through which door on a given shift, the full chain from `EnergyUnit` back to `Comedian` and `ChildDoor` is traversable in a single SPARQL query. This lineage also underpins the Monsters, Inc. commitment to energy transparency: every megawatt-hour dispatched to Monstropolis can be traced to a named agent, a certified comedian, and a timestamped collection event, providing an immutable accountability chain that supports both internal audit and external regulatory reporting.

---

## Cross-References

- [04 Ontology BPM](04-ontology-bpm.md) — the OBPM process model creates the `prov:Activity` instances recorded here; each BPMN task maps to one or more PROV-O activities
- [05 Data Catalog](05-data-catalog.md) — the `EnergyLedger` DCAT dataset holds `EnergyUnit` instances such as `EU-20240315-042-001`
- [09 Constraints & Queries](09-constraints-queries.md) — SPARQL query Q8 traverses this exact lineage chain using `prov:wasDerivedFrom` and `prov:wasGeneratedBy` paths
