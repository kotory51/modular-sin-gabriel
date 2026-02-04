import sqlite3
from pathlib import Path

DB_PATH = Path("data/vehiculos.db")

ESTADOS_VALIDOS = ("Disponible", "En ruta", "Mantenimiento")


def get_conn():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS vehiculos (
            id TEXT PRIMARY KEY,
            placa TEXT UNIQUE,
            modelo TEXT,
            capacidad INTEGER,
            estado TEXT,
            tarjeta_circulacion TEXT
        )
        """)


def next_vehiculo_id():
    with get_conn() as con:
        r = con.execute("SELECT COUNT(*) c FROM vehiculos").fetchone()
        return f"VEH-{r['c'] + 1:03d}"


def fetch_vehiculos():
    with get_conn() as con:
        return [dict(r) for r in con.execute("SELECT * FROM vehiculos")]


def fetch_vehiculo_by_id(vid):
    with get_conn() as con:
        r = con.execute("SELECT * FROM vehiculos WHERE id=?", (vid,)).fetchone()
        return dict(r) if r else None


def insert_vehiculo(data):
    if data["estado"] not in ESTADOS_VALIDOS:
        raise ValueError("Estado inválido")

    with get_conn() as con:
        con.execute("""
        INSERT INTO vehiculos VALUES (?,?,?,?,?,?)
        """, (
            data["id"],
            data["placa"],
            data["modelo"],
            data["capacidad"],
            data["estado"],
            data.get("tarjeta_circulacion")
        ))


def update_vehiculo(data):
    if data["estado"] not in ESTADOS_VALIDOS:
        raise ValueError("Estado inválido")

    with get_conn() as con:
        con.execute("""
        UPDATE vehiculos SET
            placa=?,
            modelo=?,
            capacidad=?,
            estado=?,
            tarjeta_circulacion=?
        WHERE id=?
        """, (
            data["placa"],
            data["modelo"],
            data["capacidad"],
            data["estado"],
            data.get("tarjeta_circulacion"),
            data["id"]
        ))


def delete_vehiculo(vid):
    with get_conn() as con:
        con.execute("DELETE FROM vehiculos WHERE id=?", (vid,))


# ===== estados automáticos =====
def set_estado_vehiculo(vid, estado):
    if estado not in ESTADOS_VALIDOS:
        raise ValueError("Estado inválido")

    with get_conn() as con:
        con.execute(
            "UPDATE vehiculos SET estado=? WHERE id=?",
            (estado, vid)
        )
