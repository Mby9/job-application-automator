import sqlite3

con = sqlite3.connect('copilot.db')
cur = con.cursor()

try:
    print("Migrating field_mappings to drop UNIQUE constraint on label_text...")
    cur.execute('''
    CREATE TABLE field_mappings_new (
        id INTEGER NOT NULL PRIMARY KEY,
        label_text VARCHAR,
        field_value VARCHAR,
        category VARCHAR,
        status VARCHAR,
        owner_id INTEGER
    )
    ''')

    cur.execute('INSERT INTO field_mappings_new SELECT id, label_text, field_value, category, status, owner_id FROM field_mappings')
    cur.execute('DROP TABLE field_mappings')
    cur.execute('ALTER TABLE field_mappings_new RENAME TO field_mappings')
    cur.execute('CREATE INDEX ix_field_mappings_label_text ON field_mappings (label_text)')
    
    con.commit()
    print("Migration successful.")
except Exception as e:
    print(f"Migration failed: {e}")
    con.rollback()
finally:
    con.close()
