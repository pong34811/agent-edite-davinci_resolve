#!/usr/bin/env bash
# Promote approved drafts into originals, 2 timelines per call with pauses.
set -u
cd /c/Users/warit/Desktop/agent-edite-davinci_resolve || exit 1
PROJECT_ID=ad3d2d94-af43-4d99-9bc5-fed9c27a47ad
LOG=.hermes/artifacts/enrichment-review-2026-10-06-live2/promotion/driver2.log
: > "$LOG"
for pair in "5,6" "7,8" "9,10" "11,12" "13,14" "15,16" "17,18" "19,20" "21,22" "23,24" "25,26" "27,28" "29,30" "31,32" "33,34" "35,36" "37,38" "39,40" "41,42" "43,44" "45,46" "47,48" "49"; do
  echo "=== PROMOTE $pair $(date +%H:%M:%S) ===" >> "$LOG"
  if ! python -u -m scripts.promote_drafts_to_originals --ordinals "$pair" --project-id "$PROJECT_ID" --apply >> "$LOG" 2>&1; then
    echo "STOPPED_ON_FAILURE $pair" >> "$LOG"
    exit 1
  fi
  sleep 4
done
echo "ALL_PROMOTIONS_DONE" >> "$LOG"
