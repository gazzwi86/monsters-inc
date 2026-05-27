#!/bin/bash
# Validate Turtle files via rdflib after Write/Edit — guarded until uv project exists
f=$(jq -r '.tool_input.file_path // empty')
[ -z "$f" ] && exit 0
echo "$f" | grep -q '\.ttl$' || exit 0
[ -f "/Users/gareth/Sites/obpm/pyproject.toml" ] || exit 0
cd /Users/gareth/Sites/obpm || exit 0
TTL_FILE="$f" uv run python3 - <<'PYEOF' 2>&1
import os, sys, rdflib
f = os.environ["TTL_FILE"]
try:
    g = rdflib.Graph()
    g.parse(f, format="turtle")
    print(f"Turtle OK: {len(g)} triples — {os.path.basename(f)}")
except Exception as e:
    print(f"Turtle INVALID: {os.path.basename(f)}\n  {e}", file=sys.stderr)
    sys.exit(1)
PYEOF
