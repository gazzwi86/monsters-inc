---
description: Show the Monsters Inc project goal, current artifact status, and next step to execute
---

You are working on the **Monsters, Inc. Enterprise Architecture** project at `/Users/gareth/Sites/obpm`.

Do the following in order:

1. Read `CLAUDE.md` (conventions, execution order, key constraints)
2. Run this command to see what exists:
   ```
   find /Users/gareth/Sites/obpm \( -name "*.md" -o -name "*.ttl" -o -name "*.sparql" -o -name "*.py" \) \
     ! -path "*/CLAUDE.md" ! -path "*/.claude/*" \
     | sort
   ```
3. Cross-reference against the **Execution Order** table in CLAUDE.md
4. Report concisely:
   - What exists (✓) vs what's pending (○) — group by category
   - The **single next artifact** to create, with its dependencies noted
   - Any cross-reference consistency issues to be aware of

**Project goal in one sentence:** Maintain a comprehensive open-standards enterprise architecture model of Monsters, Inc. — 16 docs, 9 ontology .ttl files, 3 SHACL shapes, 1 R2RML mapping, 6 SPARQL query suites, and 9 Python scripts — demonstrating OWL 2, SKOS, SHACL, SPARQL, PROV-O, DCAT 3, R2RML, ODRL, and ArchiMate via PlantUML. The initial build is complete; this command now reports current state and the next refinement.

The original brief is preserved for reference at `.claude/prompts/spec.md` (canonical domain knowledge) and `.claude/prompts/PROMPT.md` (per-artifact content requirements). The live source of truth is now the artifacts themselves plus `CLAUDE.md`.
