#!/bin/bash
cd C:/Users/warit/Desktop/agent-edite-davinci_resolve
timeout 150 python scripts/m3_convert.py "$@" 2>&1 | grep -v "^$" | python -c "
import sys,json
for l in sys.stdin:
    l=l.strip()
    if l.startswith('{'):
        d=json.loads(l); print('  ok=',d['ok'],'stills_ok=',d['stills_ok'],'saved=',d['saved'],'subs',d['subs'],'audio',d['audio'],'gif',d['gif_ranges'],d['name'][:28])
    else: print(l[:220])
"
