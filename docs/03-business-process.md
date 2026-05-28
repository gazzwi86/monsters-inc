# Business Process — P1: Daily Laugh Run

> **View:** Process | **Standard:** BPMN (via UML Activity) | **Audience:** Operations, Process Architects

P1: Daily Laugh Run is the core value-creating process at Monsters, Inc., spanning five organisational domains and two shifts per day across 100 comedy stations. It transforms child laughter into sealed laugh canisters (~14.5 MWh each), which are extracted into grid-ready energy units by day's end.

**Navigation:** [← 02 Capability Map](02-capability-map.md) | [→ 04 Ontology BPM](04-ontology-bpm.md) | [All Views →](../README.md)

---

## Diagram 1: P1 — Daily Laugh Run (Swim Lane)

<!-- diagram-image -->
![P1 — Daily Laugh Run (BPMN Swim Lane)](../images/diagrams/03-business-process__1__P1-Daily-Laugh-Run.png)

```plantuml
@startuml P1-Daily-Laugh-Run
!theme plain
skinparam backgroundColor #FFFFFF
skinparam swimlaneBorderColor #666666
skinparam ArrowColor #333333
skinparam ActivityBorderColor #333333
skinparam ActivityBackgroundColor #F5F5F5
skinparam ActivityDiamondBackgroundColor #FFF9C4
skinparam NoteBackgroundColor #E8F5E9

title P1 — Daily Laugh Run (BPMN Swim Lane)

|DISPATCHER (D2)|
start
:Shift Start — two shifts per day;
:Issue 100 door activation\nrequests to Door Technicians;

|DOOR TECHNICIAN (D3)|
:Retrieve assigned door\nfrom vault;
if (Quality Check) then (pass)
    :Install door at\nLaugh Floor station;
else (fail)
    :Quarantine door\n(status → quarantined);
    :Request replacement\ndoor from vault;
    -[#red]-> Retrieve assigned door\nfrom vault;
endif

|COMEDIAN (D2)|
:Receive brief —\ndoor code, child profile,\ntechnique guidance;
:Enter child's bedroom\nthrough activated door;
:Perform comedy routine;
:Laugh energy captured\nin canister;
:Return through door\nwith filled canister;
:Seal canister;

|ENERGY STATION (D1)|
:Receive sealed canister\nat station;
:Scan barcode;
:Extract energy\nfrom canister;
:Log EnergyUnit\nto grid ledger;

|DOOR TECHNICIAN (D3)|
:Remove door\nfrom station;
:Log door return;
:Return door to vault;
:Schedule next\nmaintenance window;

|CDA MONITOR (D5)|
:Automated compliance check\nper station;
if (ContaminationAlert?) then (yes — 2319 detected)
    :Trigger Protocol 2319\n(subprocess → P5); <<#pink>>
    note right
        CDA notified within
        30 minutes of detection
    end note
elseif (Comedian below\nmin laugh threshold?) then (yes)
    :Station paused; <<#pink>>
    :Supervisor intervention\nand assessment;
else (clear)
endif

|DISPATCHER (D2)|
:Close shift;
:Aggregate performance data\nfrom all 100 stations;
:Create PerformanceRecord\nper Comedian;
stop

@enduml
```

---

## Diagram 2: Exception Flows

<!-- diagram-image -->
![P1 — Exception Flows](../images/diagrams/03-business-process__2__P1-Exception-Flows.png)

```plantuml
@startuml P1-Exception-Flows
!theme plain
skinparam backgroundColor #FFFFFF
skinparam ArrowColor #333333
skinparam ActivityBorderColor #333333
skinparam ActivityBackgroundColor #F5F5F5
skinparam ActivityDiamondBackgroundColor #FFF9C4
skinparam NoteBackgroundColor #FFE0E0

title P1 — Exception Flows

|EX1 — Door Quality Failure|
start
:Door retrieved from vault;
if (Quality check) then (fail)
    :Door quarantined;
    note right
        Status → quarantined
        Removed from active pool
    end note
    :Replacement requested\nfrom vault;
    :Replacement door retrieved\nand re-checked;
    if (Quality check) then (pass)
        :Door installed at station;
    else (fail again)
        :Escalate to\nDoor Management supervisor;
    endif
else (pass)
    :Normal installation proceeds;
endif
stop

|EX2 — CDA 2319 Contamination|
start
:CDA Monitor detects\nContaminationAlert at station;
:Station immediately sealed;
note right
    Human world contact
    triggers mandatory
    Protocol 2319
end note
:Subprocess P5 activated —\nCDA Decontamination Protocol;
:Affected Comedian isolated\nfor hazmat debrief;
:CDA incident record created;
:Incident resolved and\nclosed within 30 minutes;
stop

|EX3 — Below Laugh Threshold|
start
:CDA Monitor detects\nComedian below\nminimum laugh threshold;
:Station performance flag raised;
note right
    Laugh score < minimum
    triggers operational hold
end note
:Station paused;
:Supervisor notified;
:Assessment conducted —\ntechnique review;
if (Resumption approved?) then (yes)
    :Station resumes;
else (no)
    :Comedian reassigned;\nStation held for shift;
endif
stop

@enduml
```

---

## Process Steps

| Step | Actor | Domain | Creates / Modifies |
|------|-------|--------|--------------------|
| S1 — Issue door activation requests | Dispatcher | D2 Laugh Operations | 100 activation requests issued |
| S2 — Retrieve door from vault | Door Technician | D3 Door Management | ChildDoor retrieved; quality check performed |
| S3 — Install door at station | Door Technician | D3 Door Management | ChildDoor status → active at LaughFloorStation |
| S4 — Receive brief and perform routine | Comedian | D2 Laugh Operations | Laugh energy captured in LaughCanister |
| S5 — Seal canister | Comedian | D2 Laugh Operations | LaughCanister sealStatus → true |
| S6 — Extract energy and log EnergyUnit | Energy Station | D1 Energy Production | EnergyUnit created; grid ledger updated |
| S7 — Remove door and return to vault | Door Technician | D3 Door Management | ChildDoor status → maintenance; vault record updated |
| S8 — Automated compliance check | CDA Monitor | D5 CDA Compliance | CDAIncident created (if triggered); station flagged |
| S9 — Close shift and aggregate data | Dispatcher | D2 Laugh Operations | PerformanceRecord created per Comedian |

---

## Semantic Definition

P1 is not only a diagram: it is a `mi:BusinessProcess` individual in `ontologies/mi-process.ttl`, carrying its trigger event and the artefacts it produces and consumes, so the process can be reasoned over by SPARQL and the agent authority model in Doc 13.

<!-- excerpt-from: ontologies/mi-process.ttl -->
```turtle
mi:P1_DailyLaughRun a mi:BusinessProcess ;
    rdfs:label       "P1 — Daily Laugh Run" ;
    mi:triggeredBy   mi:ShiftStartEvent ;
    mi:produces      mi:PerformanceRecord, mi:EnergyUnit ;
    mi:consumesInput mi:ChildDoor, mi:LaughCanister ;
```

---

## Why This Matters

Modeling P1 with swim lanes makes the five-domain coordination explicit: Laugh Operations, Door Management, Energy Production, and CDA Compliance must hand off control at precise points in every shift, and a failure at any hand-off (a quarantined door, a sub-threshold Comedian, a contamination alert) propagates side-effects across domain boundaries. Without this process view, the cross-domain dependencies remain tacit and unmeasurable. Exposing them in a shared notation — BPMN-style activity lanes — gives architects, operations managers, and compliance officers a common language for designing controls, SLAs, and exception-handling procedures around the same artefact.

---

## Cross-References

- [04 Ontology BPM](04-ontology-bpm.md) — this process annotated with OWL semantics, linking each step to its domain class and property chain
- [09 Constraints & Queries](09-constraints-queries.md) — SHACL shapes enforce pre-conditions for dispatch (certified Comedian, active ChildDoor, maintenance date in range)
- [06 Data Lineage](06-data-lineage.md) — PROV-O traces the laugh → canister → EnergyUnit → grid lineage chain originating in P1
