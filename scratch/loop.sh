#!/bin/bash
cd C:/Users/warit/Desktop/agent-edite-davinci_resolve
for b in "$@"; do
  echo "##### batch $b"
  scratch/runbatch.sh $b
  python - <<'PY'
import json
r=json.load(open("scratch/m3/results.json",encoding="utf-8"))
bad=[k for k,v in r.items() if not (v["ok"] and v["stills_ok"] and v["saved"]) and k!="8"]
print("done:",sorted(map(int,r))[-1],"count",len(r),"bad:",bad, "eyeball:",{k:v.get("needs_eyeball") for k,v in r.items() if v.get("needs_eyeball")})
raise SystemExit(3 if bad else 0)
PY
  [ $? -ne 0 ] && break
  sleep 45
done
