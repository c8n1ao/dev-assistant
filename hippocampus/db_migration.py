"""海马体数据库迁移脚本 — 保留用于未来 schema 升级"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "memory.db"

def migrate():
    """执行所有待执行的迁移"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    # 迁移逻辑在此追加
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
