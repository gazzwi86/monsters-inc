#!/bin/bash
# Validate SPARQL query files via rdflib after Write/Edit — guarded until uv project exists
f=$(jq -r '.tool_input.file_path // empty')
[ -z "$f" ] && exit 0
echo "$f" | grep -q '\.sparql$' || exit 0
[ -f "/Users/gareth/Sites/obpm/pyproject.toml" ] || exit 0
cd /Users/gareth/Sites/obpm || exit 0
SPARQL_FILE="$f" uv run python3 - <<'PYEOF' 2>&1
import os, sys, re
from rdflib.plugins.sparql import prepareQuery
f = os.environ["SPARQL_FILE"]
try:
    content = open(f).read()
    # Split on lines that start a new query (PREFIX, SELECT, CONSTRUCT, ASK, DESCRIBE)
    blocks = re.split(r'\n(?=PREFIX\b|SELECT\b|CONSTRUCT\b|ASK\b|DESCRIBE\b)', content.strip())
    queries = [b.strip() for b in blocks if b.strip() and not b.strip().startswith('#')]
    count = 0
    for q in queries:
        prepareQuery(q)
        count += 1
    noun = "query" if count == 1 else "queries"
    print(f"SPARQL OK: {count} {noun} — {os.path.basename(f)}")
except Exception as e:
    print(f"SPARQL INVALID: {os.path.basename(f)}\n  {e}", file=sys.stderr)
    sys.exit(1)
PYEOF
