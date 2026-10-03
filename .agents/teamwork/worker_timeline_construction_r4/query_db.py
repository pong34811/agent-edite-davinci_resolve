import sqlite3

db_path = r'G:\My Drive\Projects\Resolve Project Library\Resolve Projects\Users\guest\Projects\Tygarina\tygarina_2026-09-30\Project.db'
conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
cur = conn.cursor()

tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print("Tables:", tables)

for tbl in tables:
    count = cur.execute(f"SELECT count(*) FROM [{tbl}]").fetchone()[0]
    print(f"  {tbl}: {count} rows")
    if 'seq' in tbl.lower() or 'timeline' in tbl.lower() or 'proj' in tbl.lower():
        try:
            sample = cur.execute(f"SELECT * FROM [{tbl}] LIMIT 3").fetchall()
            print(f"    sample: {sample}")
        except Exception as e:
            print(f"    err: {e}")

conn.close()
