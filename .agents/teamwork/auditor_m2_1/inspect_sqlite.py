import os
import sqlite3
from datetime import datetime, timezone

db_file = r'G:\My Drive\Projects\Resolve Project Library\Resolve Projects\Users\guest\Projects\Tygarina\tygarina_2026-09-30\Project.db'
st = os.stat(db_file)
mtime = datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat()
print(f'Project.db file size: {st.st_size} bytes')
print(f'Project.db last modified UTC: {mtime}')

conn = sqlite3.connect(f'file:{db_file}?mode=ro', uri=True)
cur = conn.cursor()
tables = [row[0] for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
print(f'Total SQLite tables in Project.db: {len(tables)}')

# Search for timeline entries or sequences
for tbl in tables:
    if any(k in tbl.lower() for k in ['timeline', 'sequence', 'item', 'clip']):
        cnt = cur.execute(f'SELECT count(*) FROM "{tbl}"').fetchone()[0]
        print(f'Table {tbl}: {cnt} rows')

# Look for SM_Sequence or similar tables to find timeline names
if 'SM_Sequence' in tables:
    rows = cur.execute('SELECT * FROM SM_Sequence').fetchall()
    print(f'\nSM_Sequence count: {len(rows)}')
    for r in rows:
        print(r)

# Look for project metadata
for tbl in tables:
    if 'project' in tbl.lower():
        print(f'\nSample from {tbl}:')
        try:
            for r in cur.execute(f'SELECT * FROM "{tbl}" LIMIT 5').fetchall():
                print(r)
        except Exception as e:
            print(e)

conn.close()
