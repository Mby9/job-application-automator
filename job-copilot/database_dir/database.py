from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import DATABASE_URL
import logging

logger = logging.getLogger("copilot.database")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)


class FieldMapping(Base):
    __tablename__ = "field_mappings"

    id = Column(Integer, primary_key=True, index=True)
    label_text = Column(String, index=True)
    field_value = Column(String)
    category = Column(String, nullable=True)
    status = Column(String, default="pending")  # pending | active
    owner_id = Column(Integer, nullable=True) # ForeignKey to user.id


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    company = Column(String)
    url = Column(String)
    description = Column(Text)
    location = Column(String, nullable=True)
    match_score = Column(Integer, nullable=True)
    ats_source = Column(String, nullable=True)   # greenhouse | lever | ashby | workday
    is_priority = Column(Boolean, default=False)
    status = Column(String, default="discovered")  # discovered, applied, rejected
    posted_at = Column(String, nullable=True)      # ISO8601 or plain string
    salary_range = Column(String, nullable=True)
    owner_id = Column(Integer, nullable=True) # ForeignKey to user.id

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    ats_type = Column(String)       # greenhouse | lever | ashby | workday
    board_token = Column(String)
    source_url = Column(String, nullable=True)
    status = Column(String, default="suggested")  # suggested | approved | rejected
    is_priority = Column(Boolean, default=False)
    domain = Column(String, nullable=True)
    logo_url = Column(String, nullable=True)
    owner_id = Column(Integer, nullable=True) # ForeignKey to user.id


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    preferred_locations = Column(Text, default="[]")   # JSON array
    preferred_keywords = Column(Text, default="[]")    # JSON array
    remote_only = Column(Boolean, default=False)
    dark_mode = Column(Boolean, default=False)
    seniority_level = Column(String, default="Any")  # Any, Junior, Mid, Senior
    legal_work_country = Column(String, default="Any") # e.g. "Canada", "USA"
    owner_id = Column(Integer, nullable=True) # ForeignKey to user.id

class LabelCache(Base):
    """Caches semantic matches between page labels and saved labels"""
    __tablename__ = "label_cache"

    id = Column(Integer, primary_key=True, index=True)
    page_label = Column(String, index=True)  # e.g., "Given Name"
    stored_label = Column(String, index=True) # e.g., "First Name"

def migrate_db():
    """
    Applies additive schema changes to existing tables.
    SQLAlchemy create_all() won't ALTER existing tables, so we do it explicitly.
    SQLite ignores ALTER TABLE if the column already exists when using
    'IF NOT EXISTS' — but SQLite < 3.37 doesn't support that syntax,
    so we catch the OperationalError instead.
    """
    migrations = [
        "ALTER TABLE jobs ADD COLUMN location TEXT",
        "ALTER TABLE jobs ADD COLUMN ats_source TEXT",
        "ALTER TABLE jobs ADD COLUMN is_priority INTEGER DEFAULT 0",
        "ALTER TABLE user_preferences ADD COLUMN dark_mode INTEGER DEFAULT 0",
        "ALTER TABLE companies ADD COLUMN domain TEXT",
        "ALTER TABLE companies ADD COLUMN logo_url TEXT",
        "ALTER TABLE field_mappings ADD COLUMN status TEXT DEFAULT 'pending'",
        "ALTER TABLE jobs ADD COLUMN posted_at TEXT",
        "ALTER TABLE jobs ADD COLUMN salary_range TEXT",
        "ALTER TABLE user_preferences ADD COLUMN seniority_level TEXT DEFAULT 'Any'",
        "ALTER TABLE jobs ADD COLUMN owner_id INTEGER",
        "ALTER TABLE companies ADD COLUMN owner_id INTEGER",
        "ALTER TABLE user_preferences ADD COLUMN owner_id INTEGER",
        "ALTER TABLE field_mappings ADD COLUMN owner_id INTEGER",
        "ALTER TABLE user_preferences ADD COLUMN legal_work_country TEXT DEFAULT 'Any'",
    ]
    with engine.connect() as conn:
        for stmt in migrations:
            try:
                conn.execute(text(stmt))
                conn.commit()
                logger.info("Migration applied: %s", stmt)
            except Exception as e:
                if "duplicate column" in str(e).lower():
                    logger.debug("Column already exists, skipping: %s", stmt)
                else:
                    logger.warning("Migration skipped (%s): %s", type(e).__name__, stmt)


def init_db():
    Base.metadata.create_all(bind=engine)
    migrate_db()
