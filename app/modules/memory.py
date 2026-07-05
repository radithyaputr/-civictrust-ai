"""
CivicTrust AI - Memory Module
Short-term conversation memory for natural dialogue.
"""
import logging
from typing import List, Dict, Any, Optional
from app.database.connection import database
from app.config import settings

logger = logging.getLogger(__name__)


class MemoryModule:
    """Manages conversation memory for sessions."""

    def __init__(self):
        self.max_history = settings.MAX_SESSION_HISTORY

    async def add(self, session_id: str, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to the session history."""
        try:
            import json
            await database.execute(
                """INSERT INTO messages (session_id, role, content, metadata)
                   VALUES (?, ?, ?, ?)""",
                (session_id, role, content, json.dumps(metadata or {})),
            )
            
            await database.execute(
                "UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (session_id,),
            )
        except Exception as e:
            logger.error(f"Failed to add message to memory: {e}")

    async def get_history(self, session_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get conversation history for a session."""
        try:
            limit = limit or self.max_history
            rows = await database.fetch_all(
                """SELECT role, content, timestamp, metadata
                   FROM messages
                   WHERE session_id = ?
                   ORDER BY timestamp ASC
                   LIMIT ?""",
                (session_id, limit),
            )
            
            history = []
            for row in rows:
                history.append({
                    "role": row["role"],
                    "content": row["content"],
                    "timestamp": row["timestamp"],
                })
            return history
        except Exception as e:
            logger.error(f"Failed to get history: {e}")
            return []

    async def get_context(self, session_id: str) -> Dict[str, Any]:
        """Get conversation context for the orchestrator."""
        history = await self.get_history(session_id, limit=10)
        return {
            "session_id": session_id,
            "message_count": len(history),
            "recent_messages": history[-5:] if history else [],
            "has_history": len(history) > 0,
        }

    async def clear(self, session_id: str):
        """Clear conversation history for a session."""
        try:
            await database.execute(
                "DELETE FROM messages WHERE session_id = ?",
                (session_id,),
            )
        except Exception as e:
            logger.error(f"Failed to clear memory: {e}")

    async def ensure_session(self, session_id: str, user_id: Optional[str] = None, language: str = "id"):
        """Create a session if it doesn't exist."""
        try:
            await database.execute(
                """INSERT OR IGNORE INTO sessions (id, user_id, language)
                   VALUES (?, ?, ?)""",
                (session_id, user_id, language),
            )
        except Exception as e:
            logger.error(f"Failed to ensure session: {e}")

    async def create_session(self, session_id: str, user_id: Optional[str] = None, language: str = "id"):
        """Create a new session (alias for ensure_session)."""
        await self.ensure_session(session_id, user_id, language)