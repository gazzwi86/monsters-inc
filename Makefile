.PHONY: all ontology validate query query-cv query-agent query-human query-gov query-con query-all catalog seed demo install status query-one drift

BANNER = @echo "──────────────────────────────────────────" && echo "  Monsters, Inc. — $(1)" && echo "──────────────────────────────────────────"

all: seed ontology validate query query-cv query-agent query-human query-gov query-con
	@echo "✓ All artifacts built and verified"

demo: install seed ontology
	@echo "Demo data loaded. Run 'make query' or 'make Q=Q1 query-one' to explore."

ontology:
	$(call BANNER,Generating OWL Ontology)
	uv run mi-ontology

seed:
	$(call BANNER,Seeding Instance Data)
	uv run mi-seed

validate:
	$(call BANNER,SHACL Validation — expect 3 violations)
	uv run mi-validate

query:
	$(call BANNER,Running Business SPARQL Queries)
	uv run mi-query

query-cv:
	$(call BANNER,Compliance Violation Queries)
	uv run mi-query --file compliance-violations.sparql

query-agent:
	$(call BANNER,Agent Authority Queries)
	uv run mi-query --file agent-authority.sparql

query-human:
	$(call BANNER,Human-Centered Queries)
	uv run mi-query --file human-centered.sparql

query-gov:
	$(call BANNER,Data Governance Queries)
	uv run mi-query --file governance.sparql

query-con:
	$(call BANNER,Constitution & Defensibility Queries)
	uv run mi-query --file constitution.sparql

query-all: query query-cv query-agent query-human query-gov query-con
	@echo "✓ All query suites executed"

catalog:
	$(call BANNER,Building DCAT Catalog)
	uv run mi-catalog

install:
	uv sync

query-one:
	@echo "Running query $(Q)..."
	uv run mi-query --query $(Q)

drift:
	$(call BANNER,Doc/Source Drift Check)
	uv run python scripts/check_doc_drift.py

status:
	$(call BANNER,Artifact Progress)
	@printf "  docs:       %2s/16\n"  "$$(find docs -name '*.md' 2>/dev/null | wc -l | tr -d ' ')"
	@printf "  ontologies: %2s/9\n"   "$$(find ontologies -name '*.ttl' 2>/dev/null | wc -l | tr -d ' ')"
	@printf "  shapes:     %2s/3\n"   "$$(find shapes -name '*.ttl' 2>/dev/null | wc -l | tr -d ' ')"
	@printf "  mappings:   %2s/1\n"   "$$(find mappings -name '*.ttl' 2>/dev/null | wc -l | tr -d ' ')"
	@printf "  queries:    %2s/6\n"   "$$(find queries -name '*.sparql' 2>/dev/null | wc -l | tr -d ' ')"
	@printf "  scripts:    %2s/7\n"   "$$(find scripts -name '*.py' 2>/dev/null | wc -l | tr -d ' ')"
