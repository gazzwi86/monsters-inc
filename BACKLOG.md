# Backlog — leftover and optional work (plain-English)

This is a to-do list you can pick up cold, months from now, having forgotten
everything. Each item explains **what it is in simple terms** before any detail.

**First, the big picture.** This project is a pretend company — Monsters, Inc. —
modelled as a "knowledge graph": a big web of facts written in standard data
formats so that software (and AI agents) can read the company's rules and act
safely within them. Everything below is **optional polish or deferred extras**.
The project already works: running `make all` builds and checks everything and
passes. Nothing here is broken or half-done.

---

## Mini-glossary (what the jargon means)

- **`.ttl` files** (in `ontologies/`) — the model itself, written in "Turtle".
  Think of them as the spreadsheets of facts and definitions.
- **SHACL** (files in `shapes/`) — automatic rules that check the data and
  complain when something is wrong. We deliberately leave 3 broken records in the
  data so we can see the checker catch them ("3 intentional violations").
- **SPARQL** (files in `queries/`) — saved questions you can ask the data. They're
  grouped into "suites", each run by a `make` command:
  - `make query` → **business** questions (named Q1, Q2, …)
  - `make query-cv` → **compliance** questions (CV1, CV2, …)
  - `make query-agent` → **agent** questions (AA1, …) — what an AI agent is allowed to do
  - `make query-human` → **human/wellbeing** questions (HC1, …)
  - `make query-gov` → **governance** questions (GV1, …) — who can access what data
  - `make query-con` → **constitution** questions (CN1, …) — our principles and whether we enforce them
- **SKOS** (`ontologies/mi-glossary.ttl`) — a controlled dictionary of terms.
- **DCAT** (`ontologies/mi-catalog.ttl`) — a catalogue that lists our datasets.
- **ODRL** (in `ontologies/mi-governance.ttl`) — machine-readable access rules:
  "role X may *read* dataset Y; nobody may *share* it externally."
- **R2RML** (`mappings/mi-db.r2rml.ttl`) — instructions for turning a normal SQL
  database into graph facts.
- **`make <something>`** — runs a command. See the list at the very bottom.

**Priority key:** ⭐ nice-to-have · ⭐⭐ worth doing · (none here are urgent).

---

## 1. Add "C4" architecture diagrams for the systems ⭐

**What it is, plainly:** C4 is a popular way to draw software systems at four
zoom levels (whole-context → containers → components → code). We already describe
our IT systems in `docs/07-service-catalog.md`, but with ArchiMate-style diagrams,
not C4. This item is just "draw a few more diagrams, C4-style."

**Why it's here:** You said it's a nice extra for richer documentation, not urgent.

**To do it:**
- The 12 systems already exist as data in `ontologies/mi-governance.ttl` (look for
  `mi:ApplicationService` and `mi:TechnologyService`, e.g. `mi:LFMS`). Their
  links are `mi:dependsOn`, `mi:servesDomain`, `mi:accessesDataset`.
- Add 3 PlantUML diagrams (in `docs/07-service-catalog.md` or a new
  `docs/16-c4-views.md`): one "big picture", one "the systems and how they
  connect", one "zoom into one system (e.g. LFMS)".
- Diagrams are written as ```plantuml code blocks. Render them with the local
  PlantUML server you mentioned (`localhost:8080`) to check they look right.

**Done when:** the diagrams render correctly and are linked from the docs.

---

## ~~2. Fix a name clash on "EnergyLedger"~~ ✅ DONE

The glossary **term** was renamed to `mi:EnergyLedgerConcept` (in
`ontologies/mi-glossary.ttl`), and the `skos:narrower`/`skos:related` references that
pointed at it (under `mi:LaughEnergy`, `mi:GridDispatch`, `mi:RegulatoryReport`) were
updated to match. The **dataset** `mi:EnergyLedger` (catalogue + governance) was left
untouched. `grep -rn "mi:EnergyLedger\b" ontologies` now shows only dataset usages.
`docs/08-glossary.md` glossary table updated to read `mi:EnergyLedgerConcept`.

---

## ~~3. Tidy up two "double-labelled" terms~~ ✅ DONE

`mi:DoorStatus` and `mi:TrainingProgram` were added to the "dual-use pattern" note in
`ontologies/mi-glossary.ttl`, and each concept now carries a `skos:exactMatch` to its
own class (same URI, dual-use). `make all` and `make drift` stay green.

---

## 4. Write access rules for 3 sensitive datasets ⭐⭐

**What it is, plainly:** "Governance" = rules about who may use which data. One of
our governance questions, **GV6**, deliberately asks: *"which sensitive datasets do
NOT yet have an access rule written for them?"* Right now it finds **3 datasets**
that are marked "restricted" but have no rule saying who may use them:
`CDAIncidentLog`, `CDAComplianceReports`, `RDPrototypes`. (This isn't a bug — the
question exists precisely to find these. It's a "to-write" list.) If you want the
model to look fully complete, write an access rule for each.

**See it for yourself:** run `make query-gov` and look at the GV6 result (3 rows).

**To do it:**
- In `ontologies/mi-governance.ttl`, copy the style of the rules that already
  exist (search for `mi:ChildProfileDataPolicy` — it's an `odrl:Set` with a
  "permission" saying who may read, and a "prohibition" saying it can't be shared).
- Add three new rules, e.g. `mi:CDAIncidentDataPolicy` (the CDA Director may read),
  `mi:RDPrototypeDataPolicy` (the R&D Director may read), and one for compliance
  reports. Then connect each dataset to its rule with a line like:
  `mi:CDAIncidentLog mi:governedByPolicy mi:CDAIncidentDataPolicy .`

**Done when:** `make query-gov` shows **GV6 = 0 rows** (no more gaps), and `make all`
is still green.

---

## 5. Decide what to do about the "Joy over fear" principle ⭐

**What it is, plainly:** Our "constitution" lists the company's principles, and for
each one we try to attach an automatic check that proves we follow it. One
constitution question, **CN2**, asks: *"which principles have NO automatic check?"*
It finds exactly **one**: *"Joy over fear"* (the company's culture value about
laughter beating scaring). Culture values are hard to check automatically, so today
we honestly flag it as "we believe this but don't auto-check it."

**See it for yourself:** run `make query-con` and look at the CN2 result (1 row).

**To do it (only if you want zero gaps):**
- Attach it to a stand-in measurement. We already have a wellbeing question (HC5).
  In `ontologies/mi-constitution.ttl`, find `mi:Prin_JoyOverFear` and add a line:
  `mi:Prin_JoyOverFear mi:enforcedByQuery "HC5" .`

**Done when:** `make query-con` shows **CN2 = 0 rows**.

---

## 6. Make the database-conversion test run automatically ⭐

**What it is, plainly:** We have a test (`make materialize`) that takes our R2RML
instructions, builds a small real SQL database, converts it to graph facts, and
checks the result matches our hand-made data. It works, but it needs some heavy
extra software, so it does NOT run as part of `make all` — you have to remember to
run it. This item is "make it run automatically so a future mistake gets caught."

**Why it's here:** Convenience/safety, not correctness — the test passes today.

**To do it:**
- In `pyproject.toml`, add an optional dependency group:
  ```
  [dependency-groups]
  r2rml = ["morph-kgc", "sqlalchemy"]
  ```
- Change the `materialize` target in the `Makefile` to use that group, and add
  `materialize` to the `all` target. Trade-off: `make all` gets slower and pulls
  the heavy software.

**Done when:** `make all` runs the materialise test and stays green.

---

## ~~7. Put the project on GitHub~~ ✅ DONE

Pushed to **https://github.com/gazzwi86/monsters-inc** via the `git@github.com:gazzwi86/monsters-inc.git`
SSH remote (`origin`). The refinement pass landed as a single commit on `main`.

---

## ~~8. Use the official wording for one access-rule action~~ ✅ DONE

All `odrl:read` actions in `ontologies/mi-governance.ttl` were replaced with the
official `odrl:use`. GV4 doesn't filter on the action so it still returns all rules;
`make query-gov` and `make all` stay green.

---

## Cheat-sheet — commands to check things

```bash
make all          # build + check EVERYTHING (should pass). Run this after any change.
make validate     # the rule-checker; should show exactly 3 deliberate problems
make test         # 7 small logic tests
make materialize  # the database-conversion test (needs extra software; see item 6)
make drift        # checks the docs haven't drifted from the real files
make query-gov    # governance questions — GV6 shows the gaps in item 4
make query-con    # constitution questions — CN2 shows the gap in item 5
make status       # how many files of each kind exist
```

**Where the history lives:** the executed remediation plan is in
`.claude/plans/council-review-2026-05-27-round2.md`; the commit history is in
`git log` (the messages explain what changed and why).
