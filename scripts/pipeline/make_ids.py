"""Write ids.json ({"<index>": {"orig": "<timeline unique id>"}}) from timelines.json made by dump_timelines.py.
Usage: python scripts/pipeline/make_ids.py <work dir>"""
import json
import os
import sys

w = sys.argv[1]
d = json.load(open(os.path.join(w, "timelines.json"), encoding="utf-8"))
json.dump({str(x["i"]): {"orig": x["id"]} for x in d}, open(os.path.join(w, "ids.json"), "w"))
print(len(d), "timelines")
