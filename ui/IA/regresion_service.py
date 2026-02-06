from datetime import datetime
from typing import Dict, Optional
from database.db_service import get_db_service


class RegressionService:
    """Servicio para almacenar resultados de regresión lineal"""

    def __init__(self):
        self.db = get_db_service("data/device_data.db")
        self._init_db()

    def _init_db(self):
        with self.db.get_connection() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS regression_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                sensor TEXT NOT NULL,
                window_size INTEGER NOT NULL,
                slope REAL NOT NULL,
                r2 REAL,
                prediction REAL,
                trend TEXT,
                risk_level TEXT,
                timestamp TEXT NOT NULL
            )
            """)
            conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_reg_device_time
            ON regression_results (device_id, sensor, timestamp DESC)
            """)
            conn.commit()

    def save_result(self, data: Dict) -> int:
        data.setdefault("timestamp", datetime.now().isoformat())

        query = """
        INSERT INTO regression_results (
            device_id, sensor, window_size,
            slope, r2, prediction,
            trend, risk_level, timestamp
        ) VALUES (
            :device_id, :sensor, :window_size,
            :slope, :r2, :prediction,
            :trend, :risk_level, :timestamp
        )
        """
        return self.db.execute_insert(query, data)

    def get_latest(self, device_id: str, sensor: str) -> Optional[Dict]:
        query = """
        SELECT * FROM regression_results
        WHERE device_id = ? AND sensor = ?
        ORDER BY timestamp DESC
        LIMIT 1
        """
        return self.db.execute_one(query, (device_id, sensor))
