---
description: Show the Monsters Inc project goal, current artifact status, and next step to execute
---

You are working on the **Monsters, Inc. Enterprise Architecture** project at `/Users/gareth/Sites/obpm`.

Do the following in order:

1. Read `CLAUDE.md` (conventions, execution order, key constraints)
2. Run this command to see what exists:
   ```
   find /Users/gareth/Sites/obpm \( -name "*.md" -o -name "*.ttl" -o -name "*.sparql" -o -name "*.py" \) \
     ! -path "*/CLAUDE.md" ! -path "*/spec.md" ! -path "*/PROMPT.md" ! -path "*/.claude/*" \
     | sort
   ```
3. Cross-reference against the **Execution Order** table in CLAUDE.md
4. Report concisely:
   - What exists (✓) vs what's pending (○) — group by category
   - The **single next artifact** to create, with its dependencies noted
   - Any cross-reference consistency issues to be aware of

**Project goal in one sentence:** Generate 29 artifacts (13 docs, 6 ontology .ttl files, 2 SHACL shapes, 1 R2RML mapping, 2 SPARQL query files, 5 Python scripts) that together form a comprehensive open-standards enterprise architecture model of Monsters, Inc. — demonstrating OWL 2, SKOS, SHACL, SPARQL, PROV-O, DCAT 3, R2RML, and ArchiMate via PlantUML.

Use `PROMPT.md` as the authoritative spec for each artifact's content requirements.
