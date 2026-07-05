"""
CivicTrust AI - Database Connection
Handles database connectivity (SQLite for dev, PostgreSQL/Supabase for production).
"""
import asyncio
import os
import sqlite3
from typing import Optional
from app.config import settings


class Database:
    """Database connection manager with async support."""

    def __init__(self):
        self._connection: Optional[sqlite3.Connection] = None
        self._lock = asyncio.Lock()
        self.db_path = settings.DATABASE_URL.replace("sqlite:///", "")

    async def connect(self):
        """Establish database connection."""
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        self._connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA busy_timeout=5000")
        await self._create_tables()

    async def disconnect(self):
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None

    async def _create_tables(self):
        """Create all required tables."""
        async with self._lock:
            cursor = self._connection.cursor()
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE,
                    email TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    language TEXT DEFAULT 'id',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active INTEGER DEFAULT 1
                );
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                );
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    source TEXT,
                    source_type TEXT,
                    language TEXT DEFAULT 'id',
                    content_hash TEXT,
                    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                );
                CREATE TABLE IF NOT EXISTS fact_checks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    statement TEXT,
                    verdict TEXT,
                    confidence REAL,
                    sources TEXT,
                    explanation TEXT,
                    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query_count INTEGER DEFAULT 0,
                    accuracy REAL DEFAULT 0.0,
                    precision REAL DEFAULT 0.0,
                    recall REAL DEFAULT 0.0,
                    hallucination_rate REAL DEFAULT 0.0,
                    citation_coverage REAL DEFAULT 0.0,
                    avg_latency REAL DEFAULT 0.0,
                    trust_score_avg REAL DEFAULT 0.0,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    message_id INTEGER,
                    rating INTEGER,
                    comment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);
                CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
                CREATE INDEX IF NOT EXISTS idx_fact_checks_checked ON fact_checks(checked_at);
                CREATE INDEX IF NOT EXISTS idx_analytics_recorded ON analytics(recorded_at);
            """)
            self._connection.commit()

    async def _ensure_connected(self):
        """Auto-connect if not already connected."""
        if self._connection is None:
            await self.connect()

    async def execute(self, query: str, params: tuple = ()):
        """Execute a query and return cursor."""
        await self._ensure_connected()
        async with self._lock:
            cursor = self._connection.cursor()
            cursor.execute(query, params)
            self._connection.commit()
            return cursor

    async def fetch_one(self, query: str, params: tuple = ()):
        """Fetch a single row."""
        await self._ensure_connected()
        async with self._lock:
            cursor = self._connection.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()

    async def fetch_all(self, query: str, params: tuple = ()):
        """Fetch all rows."""
        await self._ensure_connected()
        async with self._lock:
            cursor = self._connection.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    async def fetch_val(self, query: str, params: tuple = ()):
        """Fetch a single value."""
        row = await self.fetch_one(query, params)
        if row:
            return row[0]
        return None


database = Database()