import sqlite3
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

db_path = r'G:\My Drive\Projects\Resolve Project Library\Resolve Projects\Users\guest\Projects\Tygarina\tygarina_2026-09-30\Project.db'
conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
cur = conn.cursor()

rows = cur.execute("SELECT Name, CreateTimeInSecs, ModTimeInSecs FROM Sm2Timeline ORDER BY CreateTimeInSecs ASC").fetchall()
print(f"Total timelines in Sm2Timeline: {len(rows)}")
for idx, (name, cdate, mdate) in enumerate(rows, 1):
    print(f"  {idx:02d}: {name} (create: {cdate}, mod: {mdate})")

conn.close()
