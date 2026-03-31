import sqlite3
import os

db_path = 'data/job_automator.db'
if not os.path.exists(db_path):
    print(f"Error: Database not found at {db_path}")
    exit(1)

con = sqlite3.connect(db_path)
cur = con.cursor()

try:
    print(f"Migrating jobs in {db_path} to drop UNIQUE constraint on url...")
    
    # Check if table exists
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='jobs'")
    if not cur.fetchone():
        print("Error: Table 'jobs' not found in database.")
        exit(1)

    cur.execute('''
    CREATE TABLE jobs_new (
        id INTEGER NOT NULL PRIMARY KEY,
        title VARCHAR,
        company VARCHAR,
        url VARCHAR,
        description TEXT,
        location VARCHAR,
        match_score INTEGER,
        ats_source VARCHAR,
        is_priority INTEGER DEFAULT 0,
        status VARCHAR DEFAULT 'discovered',
        posted_at VARCHAR,
        salary_range VARCHAR,
        owner_id INTEGER
    )
    ''')

    # Copy data, mapping columns carefully
    cur.execute('INSERT INTO jobs_new (id, title, company, url, description, location, match_score, ats_source, is_priority, status, posted_at, salary_range, owner_id) SELECT id, title, company, url, description, location, match_score, ats_source, is_priority, status, posted_at, salary_range, owner_id FROM jobs')
    
    cur.execute('DROP TABLE jobs')
    cur.execute('ALTER TABLE jobs_new RENAME TO jobs')
    
    con.commit()
    print("Migration successful.")
except Exception as e:
    print(f"Migration failed: {e}")
    con.rollback()
finally:
    con.close()
