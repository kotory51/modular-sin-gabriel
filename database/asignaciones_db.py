import sqlite3
from pathlib import Path
from datetime import datetime

from database.vehiculos_db import set_estado_vehiculo

DB_PATH = Path("data/asignaciones.db")

ESTADOS_VALIDOS = ("Activa", "Finalizada")


# ======================================================
def get_conn():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ======================================================
def init_db():
    with get_conn() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS asignaciones (
            id TEXT PRIMARY KEY,
            vehiculo_id TEXT NOT NULL,
            ruta_id TEXT NOT NULL,
            chofer_id TEXT NOT NULL,
            estado TEXT NOT NULL,
            fecha_inicio TEXT,
            fecha_fin TEXT
        )
        """)

        con.execute("""
        CREATE TABLE IF NOT EXISTS asignacion_insumos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asignacion_id TEXT NOT NULL,
            insumo_id TEXT NOT NULL,
            cantidad INTEGER NOT NULL
        )
        """)


# ======================================================
def next_asignacion_id():
    with get_conn() as con:
        r = con.execute(
            "SELECT COUNT(*) c FROM asignaciones"
        ).fetchone()
        return f"ASG-{r['c'] + 1:03d}"


# ======================================================
def fetch_asignaciones():
    with get_conn() as con:
        return [
            dict(r) for r in con.execute(
                "SELECT * FROM asignaciones ORDER BY fecha_inicio DESC"
            )
        ]


def fetch_asignacion_by_id(aid):
    with get_conn() as con:
        r = con.execute(
            "SELECT * FROM asignaciones WHERE id=?",
            (aid,)
        ).fetchone()
        return dict(r) if r else None


# ===================== VALIDACIONES =====================
def vehiculo_disponible(vehiculo_id):
    with get_conn() as con:
        r = con.execute("""
            SELECT 1 FROM asignaciones
            WHERE vehiculo_id=? AND estado='Activa'
        """, (vehiculo_id,)).fetchone()
        return r is None


def ruta_disponible(ruta_id):
    with get_conn() as con:
        r = con.execute("""
            SELECT 1 FROM asignaciones
            WHERE ruta_id=? AND estado='Activa'
        """, (ruta_id,)).fetchone()
        return r is None


def chofer_disponible(chofer_id):
    with get_conn() as con:
        r = con.execute("""
            SELECT 1 FROM asignaciones
            WHERE chofer_id=? AND estado='Activa'
        """, (chofer_id,)).fetchone()
        return r is None


# ===================== CRUD ============================
def insert_asignacion(data, insumos=None):
    if data["estado"] not in ESTADOS_VALIDOS:
        raise ValueError("Estado inválido")

    with get_conn() as con:
        con.execute("""
        INSERT INTO asignaciones VALUES (?,?,?,?,?,?,?)
        """, (
            data["id"],
            data["vehiculo_id"],
            data["ruta_id"],
            data["chofer_id"],
            data["estado"],
            data.get("fecha_inicio"),
            data.get("fecha_fin")
        ))

        # 🚦 VEHÍCULO PASA A EN RUTA
        set_estado_vehiculo(data["vehiculo_id"], "En ruta")

        if insumos:
            for i in insumos:
                con.execute("""
                INSERT INTO asignacion_insumos
                (asignacion_id, insumo_id, cantidad)
                VALUES (?,?,?)
                """, (
                    data["id"],
                    i["insumo_id"],
                    i["cantidad"]
                ))


# ======================================================
def finalizar_asignacion(aid):
    with get_conn() as con:
        r = con.execute(
            "SELECT vehiculo_id FROM asignaciones WHERE id=?",
            (aid,)
        ).fetchone()

        con.execute("""
        UPDATE asignaciones SET
            estado='Finalizada',
            fecha_fin=?
        WHERE id=?
        """, (
            datetime.now().isoformat(),
            aid
        ))

        # 🔓 VEHÍCULO VUELVE A DISPONIBLE
        if r:
            set_estado_vehiculo(r["vehiculo_id"], "Disponible")
