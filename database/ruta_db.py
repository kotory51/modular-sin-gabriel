import sqlite3
from pathlib import Path

DB_PATH = Path("data/rutas.db")

ESTADOS_VALIDOS = ("Disponible", "Activa", "Finalizada")


def get_conn():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS rutas (
            id TEXT PRIMARY KEY,
            origen TEXT NOT NULL,
            destino TEXT NOT NULL,
            distancia INTEGER,
            estado TEXT NOT NULL
        )
        """)


def next_ruta_id():
    with get_conn() as con:
        r = con.execute("SELECT COUNT(*) c FROM rutas").fetchone()
        return f"RUT-{r['c'] + 1:03d}"


def fetch_rutas():
    with get_conn() as con:
        return [dict(r) for r in con.execute("SELECT * FROM rutas")]


def insert_ruta(data):
    with get_conn() as con:
        con.execute("""
        INSERT INTO rutas VALUES (?,?,?,?,?)
        """, (
            data["id"],
            data["origen"],
            data["destino"],
            data.get("distancia"),
            data.get("estado", "Disponible")
        ))


def update_ruta(data):
    with get_conn() as con:
        con.execute("""
        UPDATE rutas SET
            origen=?,
            destino=?,
            distancia=?,
            estado=?
        WHERE id=?
        """, (
            data["origen"],
            data["destino"],
            data.get("distancia"),
            data["estado"],
            data["id"]
        ))


def delete_ruta(rid):
    with get_conn() as con:
        con.execute("DELETE FROM rutas WHERE id=?", (rid,))


def set_estado_ruta(rid, estado):
    if estado not in ESTADOS_VALIDOS:
        raise ValueError("Estado inválido")

    with get_conn() as con:
        con.execute(
            "UPDATE rutas SET estado=? WHERE id=?",
            (estado, rid)
        )
