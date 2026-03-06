#!/bin/bash
# Typecheck script that filters out errors from node_modules
# Doing this because frappe-ui has a lot of errors that are not related to our code
OUTPUT=$(vue-tsc --noEmit 2>&1)
ERRORS=$(echo "$OUTPUT" | grep -E "^(src/|error TS)" | grep -v "node_modules/")

if [ -n "$ERRORS" ]; then
  echo "$ERRORS"
  exit 1
else
  echo "Type check completed successfully (node_modules errors ignored)"
  exit 0
fi