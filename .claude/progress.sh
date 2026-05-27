#!/bin/bash
# Artifact progress counter — shown at end of each Claude session
BASE=/Users/gareth/Sites/obpm
docs=$(find "$BASE/docs"       -maxdepth 1 -name "*.md"     2>/dev/null | wc -l | tr -d ' ')
onto=$(find "$BASE/ontologies" -maxdepth 1 -name "*.ttl"    2>/dev/null | wc -l | tr -d ' ')
shps=$(find "$BASE/shapes"     -maxdepth 1 -name "*.ttl"    2>/dev/null | wc -l | tr -d ' ')
maps=$(find "$BASE/mappings"   -maxdepth 1 -name "*.ttl"    2>/dev/null | wc -l | tr -d ' ')
qrys=$(find "$BASE/queries"    -maxdepth 1 -name "*.sparql" 2>/dev/null | wc -l | tr -d ' ')
scrs=$(find "$BASE/scripts"    -maxdepth 1 -name "*.py"     2>/dev/null | wc -l | tr -d ' ')
total=$(( docs + onto + shps + maps + qrys + scrs ))

msg=$(printf "Monsters Inc. artifacts: docs %s/13 · ontologies %s/6 · shapes %s/2 · mappings %s/1 · queries %s/2 · scripts %s/5 · total %s/29" \
  "$docs" "$onto" "$shps" "$maps" "$qrys" "$scrs" "$total")

jq -n --arg m "$msg" '{"systemMessage": $m}'
