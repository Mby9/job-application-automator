import sqlite3

con = sqlite3.connect('copilot.db')
cur = con.cursor()

try:
    print("Migrating jobs to drop UNIQUE constraint on url...")
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

    cur.execute('INSERT INTO jobs_new SELECT id, title, company, url, description, location, match_score, ats_source, is_priority, status, posted_at, salary_range, owner_id FROM jobs')
    cur.execute('DROP TABLE jobs')
    cur.execute('ALTER TABLE jobs_new RENAME TO jobs')
    
    con.commit()
    print("Migration successful.")
except Exception as e:
    print(f"Migration failed: {e}")
    con.rollback()
finally:
    con.close()
