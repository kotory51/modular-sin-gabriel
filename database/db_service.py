"""
Servicio centralizado de base de datos para toda la aplicación.
Proporciona acceso uniforme a todas las funcionalidades de BD.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

class DatabaseService:
    """Gestor centralizado de conexiones y operaciones de base de datos"""
    
    def __init__(self, db_path: str = "data/device_data.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexiones a la BD (sin auto-commit)"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        except Exception as e:
            conn.rollback()
            print(f"[DB ERROR] {str(e)}")
            raise
        finally:
            conn.close()
    
    def execute_query(self, query: str, params = ()) -> List[Dict]:
        """Ejecuta una consulta SELECT y retorna resultados"""
        with self.get_connection() as conn:
            if isinstance(params, dict):
                cursor = conn.execute(query, params)
            else:
                cursor = conn.execute(query, params or ())
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_one(self, query: str, params = ()) -> Optional[Dict]:
        """Ejecuta una consulta SELECT y retorna un solo resultado"""
        results = self.execute_query(query, params)
        return results[0] if results else None
    
    def execute_insert(self, query: str, params = ()) -> int:
        """Ejecuta INSERT y retorna el ID insertado
        
        Args:
            query: SQL query con ? o :named_param
            params: tupla, diccionario o vacío
        """
        with self.get_connection() as conn:
            if isinstance(params, dict):
                cursor = conn.execute(query, params)
            elif isinstance(params, (list, tuple)):
                cursor = conn.execute(query, params)
            else:
                cursor = conn.execute(query)
            conn.commit()
            return cursor.lastrowid
    
    def execute_update(self, query: str, params = ()) -> int:
        """Ejecuta UPDATE y retorna filas afectadas
        
        Args:
            query: SQL query con ? o :named_param
            params: tupla, diccionario o vacío
        """
        with self.get_connection() as conn:
            if isinstance(params, dict):
                cursor = conn.execute(query, params)
            elif isinstance(params, (list, tuple)):
                cursor = conn.execute(query, params)
            else:
                cursor = conn.execute(query)
            conn.commit()
            return cursor.rowcount
    
    def execute_insert_batch(self, query: str, param_list: List[tuple]) -> int:
        """Ejecuta múltiples INSERT en una transacción"""
        with self.get_connection() as conn:
            cursor = conn.executemany(query, param_list)
            conn.commit()
            return cursor.rowcount

# Instancia global del servicio
_db_service: Optional[DatabaseService] = None

def get_db_service(db_path: str = "data/device_data.db") -> DatabaseService:
    """Obtiene la instancia global del servicio de BD"""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService(db_path)
    return _db_service
