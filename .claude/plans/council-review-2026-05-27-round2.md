# Monsters, Inc. EA — Council Review Round 2 (Execution Scope)

**Produced:** 2026-05-27
**Council (6 seats, opus):** AI Agent Architect · Ontology/KG Engineer · Compliance & Risk Officer · Enterprise Architect · People & Process Manager · Human-Centered Analyst
**Context:** Phases 1–2 of the prior plan are executed (`make all` passes, 2 intentional violations). This round assessed the *current* state against the downstream aim: **AI agents that reason over the company, operate within its rules, protect sensitive data, and escalate to the right human (HITL) — across all 6 strategic pillars.**

**Headline:** The model parses and the demo runs, but several **regulatory rules are silently dead or unfireable**, the **agent-authority layer is loaded-but-unconsumed**, and the model is **output-centric with zero human-wellbeing signals**. Verdicts: Agent Architect = *partial*; Compliance = *inadequate*; Ontology = *unsound*; EA = *partial*; People/Process = *partial*; Human-Centered = *output-centric*.

---

## Group A — Compliance & correctness bugs (P1 — must fix)

| # | Defect | File(s) | Fix |
|---|--------|---------|-----|
| A1 | 30-min CDA reporting rule **silently dead** — `dateTime − dateTime` is `xsd:duration`, compared to integer `1800` → never matches; 75-min severity-5 incident NOT flagged | `shapes/mi-core.shacl.ttl:161`, `queries/compliance-violations.sparql:72` | Compare to `"PT30M"^^xsd:duration` (precedent: CV7, Q3) |
| A2 | **`make query` never runs the compliance queries** — `run_queries.py` only executes `business-questions.sparql`; CV1–CV7 are dead code (this is why A1 hid) | `scripts/run_queries.py:61`, `Makefile` | Execute `compliance-violations.sparql` too; add `make query-cv` |
| A3 | SHACL **"false-clean"** — seed asserts no `involvedDoor`/`incidentStatus`/`resolvedAt`/`reportedIn`, so DoorContaminationShape (C2), lifecycle (C4), CV4, CV7 can never fire | `scripts/seed_data.py` | Seed one full-lifecycle incident + one overdue-open incident + a quarantined door with `involvedDoor` |
| A4 | Unsound `YEAR*365+MONTH*30+DAY` date math (~5-day error at month boundaries; wrong near 30/180/365-day thresholds) | `shapes/mi-core.shacl.ttl:92-94`, Q2/Q5/Q6 in `business-questions.sparql` | Use duration comparison (`NOW() - ?d > "P180D"^^xsd:duration`) |
| A5 | `mi:CCO` labelled "Chief **Comedy** Officer" → severity-5 child incidents route to Mike, not compliance | `ontologies/mi-core.ttl:468` | Add/relabel a Chief Compliance Officer role + assign a holder |
| A6 | `ChildAgeShape` `STRSTARTS(...,"13")` misses ages 14+ | `shapes/mi-core.shacl.ttl:184`, CV6 | Numeric age extraction |
| A7 | Q6 data bug — May 2026 = 390 MWh; date-shift logic bunches records into current month | `scripts/seed_data.py:38-46` | Spread records evenly across 13 months |

## Group B — Make the agent model consumable + demonstrate (P1 — the core downstream aim; user approved "integrate + document + demonstrate")

| # | Item | File(s) |
|---|------|---------|
| B1 | Bridge authority so it resolves for a **named employee**: `mi:clearanceLevel rdfs:subPropertyOf mi:authorityLevel` (or SHACL rule) | `ontologies/mi-agent-model.ttl` |
| B2 | Bind HITL triggers to steps — assert `mi:triggeredByStep` on all 3 triggers (currently zero) | `ontologies/mi-agent-model.ttl` |
| B3 | Assert `mi:automatable` on all P2–P7 steps (~38; only P1's 11 are flagged) | `ontologies/mi-agent-model.ttl` / `mi-process.ttl` |
| B4 | Tag the 48 seed `ChildProfile` individuals with `mi:dataClassification mi:SensitivePersonalData` | `scripts/seed_data.py` |
| B5 | **Runnable proof:** `queries/agent-authority.sparql` — (a) can employee E do action A on entity-class C? (b) what HITL triggers fire at step S? (c) is step S automatable? | new file |
| B6 | Enforcement: `shapes/mi-agent.shacl.ttl` (deny disclosure of SensitivePersonalData without read+role permission; flag automation of `automatable=false`); load agent-model + process into `validate_shacl.py` | new + `scripts/validate_shacl.py` |
| B7 | Rule: severity ≥ 4 ⇒ `incidentStatus mi:Escalated`; escalation-coverage query | `shapes/`, `queries/` |
| B8 | `docs/13-agent-model.md` (2 PlantUML diagrams + runnable callout) + DCAT catalog entry + README/RUNBOOK links | docs, `mi-catalog.ttl`, README, RUNBOOK |

## Group C — Human-centered queries + Culture (P1/P2 — user's explicit emphasis: "focus on human needs… help report and help human lives")

| # | Item | File(s) |
|---|------|---------|
| C1 | New human-centered SPARQL queries: overwork / consecutive-shift; worker safety exposure (incidents → affected workers); performance-fairness variance within cert level; training-at-risk *for the worker*; equitable workload distribution; wellbeing/burnout pulse | `queries/human-centered.sparql` (new) |
| C2 | Supporting props: `mi:shiftDuration`/`mi:consecutiveShiftCount`; `mi:affectedMonster`/`mi:incidentResponder` on CDAIncident (**workers are invisible in incident data today**); `mi:renewalOffered`; `mi:WellbeingPulse` class | `ontologies/mi-core.ttl`, seed |
| C3 | **Guardrail** against naive optimization (Q1+Q4+Q13 = stack-ranking weapon): HITL fires on overwork and on bulk child-profile reads — wire `HITLTrigger`/`dataClassification` into live guardrail queries | `mi-agent-model.ttl`, `queries/` |
| C4 | Model Culture as queryable SKOS (`PsychologicalSafety`, `JoyBasedPerformance`, `ComedyNPS` under HumanResources) + `WellbeingPulse` data | `ontologies/mi-glossary.ttl`, `mi-core.ttl` |

## Group D — EA coherence & documentation (P2/P3)

| # | Item | File(s) | Tier |
|---|------|---------|------|
| D1 | Reconcile service acronyms (docs/02 EPS/EGIS/HRTS… vs docs/07 ELS/HRCP/CDACG…) | `docs/02`, `docs/07` | P2 quick |
| D2 | Fix broken cross-ref links (`09-shacl.md`, `04-obpm.md`, `11-r2rml.md`, `01-ontology.md`) | `docs/01`, `docs/08` | P2 quick |
| D3 | Reconcile query-count prose ("fifteen" vs documented set) | `docs/09` | P3 quick |
| D4 | Strategy triples (`mi:Goal`/`Driver`/`Outcome`) + `realizesCapability`/`servesGoal` → closes strategy→capability→process chain in RDF | `ontologies/mi-motivation.ttl` (new), `mi-process.ttl` | P2 deeper |
| D5 | Org-chart PlantUML in docs/00; extend `reportsTo` to mid-tier; seed `VPEnergy` + `FloorManager` holders (escalation targets currently unresolvable) | `docs/00`, seed | P2 |
| D6 | SKOS fixes: top-concept/`broader` conflict, `hasTopConcept` asymmetry, wrong `exactMatch` target | `ontologies/mi-glossary.ttl` | P2 |
| D7 | R2RML: absolute profile IRI template + align door IRI casing with seed (won't join otherwise) | `mappings/mi-db.r2rml.ttl` | P2 |
| D8 | P3/P6/P7 exceptions as `mi:hasException` triples; expand P6/P7 stubs | `ontologies/mi-process.ttl` | P3 |
| D9 | SPARQL column aliases for remaining `var0/var1` queries | `queries/business-questions.sparql` | P3 quick |
| D10 | Hygiene: remove/use orphan `mi:source`; rename Q8 `?laughActivity` | `mi-core.ttl`, queries | P3 |

---

## Verification (per project LAW)
After execution: `make all` clean; `make validate` shows the late-incident violation now caught; **compliance queries actually run**; new `agent-authority`, `human-centered`, and guardrail queries return demonstrable rows; spot-render new PlantUML diagrams; all docs cross-link.
