import aiosqlite
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path

DATABASE_PATH = "/app/data/candidates.db"
INIT_SQL_PATH = Path("/app/init.sql")


@dataclass
class Candidate:
    id: int
    name: str
    lastname: str
    email: str
    position: str
    status: str
    priority: str
    salary_offer: Optional[float]
    security_clearance: bool
    internal_notes: Optional[str]
    rejection_reason: Optional[str]
    created_at: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "lastname": self.lastname,
            "email": self.email,
            "position": self.position,
            "status": self.status,
            "priority": self.priority,
            "salary_offer": self.salary_offer,
            "security_clearance": self.security_clearance,
            "internal_notes": self.internal_notes,
            "rejection_reason": self.rejection_reason,
            "created_at": self.created_at
        }


def _row_to_candidate(row: tuple) -> Candidate:
    return Candidate(
        id=row[0], name=row[1], lastname=row[2], email=row[3],
        position=row[4], status=row[5], priority=row[6],
        salary_offer=row[7], security_clearance=bool(row[8]),
        internal_notes=row[9], rejection_reason=row[10], created_at=row[11]
    )


async def init_db():
    """Initialize database and run init.sql if empty"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Check if table exists and has data
        cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='candidates'")
        table_exists = await cursor.fetchone()
        
        if not table_exists:
            # Run init.sql to create table and seed data
            init_sql = INIT_SQL_PATH.read_text()
            await db.executescript(init_sql)
            await db.commit()
            print("✅ Database initialized from init.sql")


async def close_db():
    pass


async def get_all_candidates() -> List[Candidate]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT * FROM candidates ORDER BY id DESC")
        rows = await cursor.fetchall()
        return [_row_to_candidate(row) for row in rows]


async def get_candidate_by_id(candidate_id: int) -> Optional[Candidate]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,))
        row = await cursor.fetchone()
        return _row_to_candidate(row) if row else None


async def create_candidate(
    name: str, lastname: str, email: str, position: str,
    status: str, priority: str, salary_offer: Optional[float] = None,
    security_clearance: bool = False, internal_notes: Optional[str] = None,
    rejection_reason: Optional[str] = None
) -> Candidate:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO candidates (name, lastname, email, position, status, priority, salary_offer, security_clearance, internal_notes, rejection_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, lastname, email, position, status, priority, salary_offer, int(security_clearance), internal_notes, rejection_reason))
        await db.commit()
        
        cursor = await db.execute("SELECT * FROM candidates WHERE id = ?", (cursor.lastrowid,))
        row = await cursor.fetchone()
        return _row_to_candidate(row)


async def get_all_candidates_summary() -> str:
    """
    Get summary of all candidates for AI context.
    WARNING: Intentionally vulnerable for the lab!
    """
    candidates = await get_all_candidates()
    
    summary = "Current candidates in system:\n"
    for c in candidates:
        summary += f"- {c.name} {c.lastname}: {c.position} | Status: {c.status} | Priority: {c.priority} | Salary: ${c.salary_offer} | Clearance: {c.security_clearance}\n"
        if c.internal_notes:
            summary += f"  Internal Notes: {c.internal_notes}\n"
        if c.rejection_reason:
            summary += f"  Rejection Reason: {c.rejection_reason}\n"
    
    return summary
