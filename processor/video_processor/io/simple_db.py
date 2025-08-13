# video_processor/io/simple_db.py
import os
import mysql.connector
from mysql.connector import pooling

DB_CFG = {
    "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER", "root"),                 # istersen ayrı kullanıcı açarız
    "password": os.getenv("MYSQL_PASSWORD", ""),# ← şifreni yaz
    "database": os.getenv("MYSQL_DB", "videotext"),
}

def to_mmss(ts: float) -> str:
    ts = 0.0 if ts is None else float(ts)
    mm = int(ts) // 60
    ss = int(ts) % 60          # saniyeyi “aşağı yuvarlar” (00:56 gibi)
    return f"{mm:02d}:{ss:02d}"

class SimpleRowWriter:
    def __init__(self):
        self.pool = pooling.MySQLConnectionPool(pool_name="vp_pool", pool_size=3, **DB_CFG)

    def _conn(self):
        return self.pool.get_connection()

    def insert_detection(self, file_name: str, text: str, ts_sec: float,
                         confidence: float | None, topic: str | None = None):
        if not text or text.strip() == "":
            return
        mmss = to_mmss(ts_sec)
        with self._conn() as cnx, cnx.cursor() as cur:
            cur.execute(
                "INSERT INTO ocr_texts_simple "
                "(file_name, text, topic, duration_sec, confidence) "
                "VALUES (%s,%s,%s,%s,%s)",
                (file_name, text.strip(), topic, mmss,
                 None if confidence is None else float(confidence))
            )
            cnx.commit()

            #TRUNCATE TABLE videotext.ocr_texts_simple;
