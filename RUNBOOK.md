# Monsters, Inc. Enterprise Architecture — Runbook

A step-by-step walkthrough of the complete open-standards EA model — now extended
into an **agent-grade** model (authority, human-in-the-loop, data governance,
human-wellbeing analytics, and a queryable company constitution).

All dates are relative to "today", so the time-based queries always return data.

---

## Prerequisites

```bash
uv sync          # install all dependencies (rdflib, pyshacl, rich, typer)
```

---

## Step 1 — Full pipeline

```bash
make all
```

Runs in order: seed → ontology → validate → detector tests → all six query suites.

| Stage | Command | Expected |
|-------|---------|----------|
| Seed | `mi-seed` | Instance graph → `data/seed_graph.ttl` |
| Ontology | `mi-ontology` | Core OWL 2 schema summary table |
| Validate | `mi-validate` | **Exactly 3 violations, 0 warnings**, each named |
| Tests | `make test` | 7 detector unit tests pass (CV5/CV6/CV3 fixtures) |
| Business | `query` | Q1–Q22, rich tables |
| Compliance | `query-cv` | CV1–CV7 |
| Agent | `query-agent` | AA1–AA5 (AA4 = 0 → no escalation gaps) |
| Human | `query-human` | HC1–HC8 (incl. wellbeing + guardrails) |
| Governance | `query-gov` | GV1–GV6 (incl. ODRL audit + gap report) |
| Constitution | `query-con` | CN1–CN4 (defensibility chain) |

If validation shows anything other than the 3 named violations, stop and check the shapes/seed.

---

## Step 2 — SHACL validation (the headline)

```bash
make validate
```

Loads the seed + the core/process/agent/governance/constitution ontologies + all
shape files, and asserts the three **intentional** violations by name:

| # | Node | Shape | Why it fires |
|---|------|-------|--------------|
| 1 | `comedian/emp-009` (Randall Boggs) | `ComedianCertShape` | Assigned to a station but his certification has expired |
| 2 | `door/nyc0099` (NYC-0099) | `DoorDispatchShape` | Active station door, `lastMaintained` > 180 days |
| 3 | a Q4-2025 CDA incident | `CDAReportingShape` | Reported 75 min after detection (>30 min CDA limit) |

Violation #3 is the one the 2026 council review un-broke: the 30-minute rule had
been comparing an `xsd:duration` against an integer and silently matching nothing.

---

## Step 3 — Business questions

```bash
make query                 # Q1–Q22
make Q=Q6 query-one        # single query (12-month energy trend — now smooth)
make Q=Q16 query-one       # strategy → capability → process traceability
make Q=Q8 query-one        # PROV-O lineage: laugh → canister → energy → grid
```

Q14 (comedians with no performance records) returns 0 rows **by design** — it
confirms 100% performance coverage.

---

## Step 4 — Agent authority & human-in-the-loop

```bash
make query-agent
```

Proves an autonomous agent can consume the model safely:

| Query | Answers |
|-------|---------|
| AA1 | "May employee E do action A on entity C?" — incl. **CEO is DENIED `export` of ChildProfile** |
| AA2 | Which HITL triggers fire at each process step, who they escalate to, by when |
| AA3 | Which of the ~55 process steps are agent-executable vs human-only |
| AA4 | Escalation-coverage self-check — **0 rows = every trigger is complete** |
| AA5 | Which role may read sensitive child data (default-deny otherwise) |

See `docs/13-agent-model.md`.

---

## Step 5 — Human-centered analytics

```bash
make query-human
```

The suite that serves the **workers**, not just output:

| Query | Serves |
|-------|--------|
| HC1 / HC6 | Workload distribution & recent shift load (overwork signal) |
| HC2 | Fairness — conversion-rate spread within a cert level |
| HC3 | Whose expiring certification puts THEIR job at risk with no renewal offered |
| HC4 | Worker safety exposure — incidents linked to people, not just doors |
| HC5 | Wellbeing pulse — who is signalling low psychological safety |
| HC7 | **Guardrail:** low performers in distress → human review, never auto-action |
| HC8 | **Guardrail:** sensitive child-data minimisation |

See `docs/15-constitution.md` for how these tie to the worker-wellbeing principle.

---

## Step 6 — Data governance, identity & ODRL

```bash
make query-gov
```

| Query | Shows |
|-------|-------|
| GV1 | Identity → role → service access (incl. the agent's least-privilege service account) |
| GV2 | Services touching sensitive/restricted data + the governing ODRL policy |
| GV3 | Data classification inventory (datasets + columns) |
| GV4 | ODRL policy audit — every permission & prohibition |
| GV5 | Service dependency map |
| GV6 | **Gap report:** restricted datasets with no governing policy yet |

See `docs/14-data-governance.md`.

---

## Step 7 — The company constitution

```bash
make query-con
```

Turns "we comply" into evidence: every principle and regulatory requirement links
to the SHACL shape and SPARQL query that enforce it (CN1, CN4). CN2 honestly flags
the one aspirational principle ("Joy over fear") that is not yet enforced. CN3 shows
coverage across the six strategic pillars. See `docs/15-constitution.md`.

---

## Step 8 — Single source of truth

```bash
make drift
```

The docs no longer duplicate whole ontologies — they carry short, marked excerpts
that link to the authoritative source files. `make drift` verifies every excerpt is
still verbatim-present in its source (**0 drift expected**). The checker is
`scripts/check_doc_drift.py`.

---

## Step 9 — Tests

```bash
make test          # detector unit tests (runs inside `make all`)
make materialize   # execute the R2RML mapping against SQLite and check it joins the seed
```

`make test` exercises the detectors the main seed does not positively trigger —
CV5 (filled-unsealed canister), CV6 (aged-out door, incl. the `13+` format) — plus
a regression guard for the CV3 30-minute fix, all against isolated in-memory
fixtures so the seed and the 3-violation invariant are untouched. `make materialize`
is the only test that actually RUNS `mappings/mi-db.r2rml.ttl`: it builds a SQLite
DB from the JSON sources, materialises RDF via morph-kgc, and asserts the IRIs and
`mi:doorStatus` objects join `data/seed_graph.ttl` (it uses `uv run --with`, so
morph-kgc is not a core dependency).

---

## Step 10 — Documentation

16 views in `docs/` (00–15). Suggested order: 00 → 01 → 02 → 03 → 04 → 06 → 09,
then the agent-grade layer: **13 (agent model) → 14 (data governance) → 15 (constitution)**.

```bash
make status     # artifact counts
make catalog    # DCAT 3 inventory (now incl. the knowledge/governance models)
```

---

## Artifact map

```
ontologies/   mi-core, mi-glossary, mi-process, mi-provenance, mi-catalog,
              mi-agent-model, mi-motivation, mi-governance, mi-constitution   (9)
shapes/       mi-core.shacl, mi-compliance.shacl, mi-agent.shacl              (3)
mappings/     mi-db.r2rml.ttl  (5 table maps → RDF, IRIs aligned to the seed)
queries/      business-questions, compliance-violations, agent-authority,
              human-centered, governance, constitution                       (6 suites)
scripts/      seed_data, generate_ontology, validate_shacl, run_queries,
              build_catalog, check_doc_drift, run_tests, materialize_r2rml    (9 incl __init__)
docs/         00 … 15                                                         (16 views)
```

---

## Intentional violations (do NOT "fix" them — they prove the validator works)

| # | Entity | Violation | Rule |
|---|--------|-----------|------|
| 1 | Randall Boggs (`comedian/emp-009`) | TrainingRecord expired while assigned to a station | `ComedianCertShape` |
| 2 | Door NYC-0099 (`door/nyc0099`) | `lastMaintained` > 180 days | `DoorDispatchShape` |
| 3 | Q4-2025 CDA incident | Reported 75 min after detection (>30 min) | `CDAReportingShape` |

Seeded deliberately in `scripts/seed_data.py`.
