import aiosqlite
import logging
import uuid
from typing import Optional
from config import DB_PATH


logger = logging.getLogger(__name__)

# Global database connection
db: Optional[aiosqlite.Connection] = None


async def init_db():
    global db
    try:
        db = await aiosqlite.connect(DB_PATH)
        db.row_factory = aiosqlite.Row
        
        await create_tables()
        logger.info(f"Database initialized: {DB_PATH}")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


async def create_tables():
    if db is None:
        raise RuntimeError("Database not initialized")
    
    # Users
    await db.execute(f"""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            session_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Admins
    await db.execute(f"""
        CREATE TABLE IF NOT EXISTS admin (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    await db.commit()
    logger.info("Database tables created successfully")


async def close_db():
    global db
    if db:
        await db.close()
        db = None
        logger.info("Database connection closed")


async def create_or_update_user(user_id: int, username: Optional[str] = None,
                                first_name: Optional[str] = None,
                                last_name: Optional[str] = None,
                                session_id: Optional[str] = None):
    if db is None:
        raise RuntimeError("Database not initialized")
    
    await db.execute("""
        INSERT INTO users (user_id, username, first_name, last_name, session_id, updated_at)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username,
            first_name = excluded.first_name,
            last_name = excluded.last_name,
            session_id = COALESCE(excluded.session_id, users.session_id),
            updated_at = CURRENT_TIMESTAMP
    """, (user_id, username, first_name, last_name, session_id))
    await db.commit()


async def get_user_session(user_id: int) -> Optional[str]:
    if db is None:
        raise RuntimeError("Database not initialized")
    
    async with db.execute(
        "SELECT session_id FROM users WHERE user_id = ?",
        (user_id,)
    ) as cursor:
        row = await cursor.fetchone()
        return row[0] if row and row[0] else None


async def create_admin(user_id: int):
    if db is None:
        raise RuntimeError("Database not initialized")
    
    await db.execute("""
        INSERT INTO admin (user_id, created_at)
        VALUES (?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id) DO UPDATE SET
            created_at = CURRENT_TIMESTAMP
    """, (user_id,))
    await db.commit()


async def delete_admin(user_id: int):
    if db is None:
        raise RuntimeError("Database not initialized")

    await db.execute("""
        DELETE FROM admin WHERE user_id = ?
    """, (user_id))
    await db.commit()


async def get_admin_ids() -> list[int]:
    if db is None:
        raise RuntimeError("Database not initialized")
    
    async with db.execute(
        "SELECT user_id FROM admin"
    ) as cursor:
        rows = await cursor.fetchall()
        return [row["user_id"] for row in rows]
