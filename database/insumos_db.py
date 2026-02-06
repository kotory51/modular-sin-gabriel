import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("data/insumos.db")


def conn():
    DB_PATH.parent.mkdir(exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with conn() as c:
        # ===== INSUMOS =====
        c.execute("""
        CREATE TABLE IF NOT EXISTS insumos (
            id TEXT PRIMARY KEY,
            tipo TEXT,
            nombre TEXT,
            lote TEXT,
            registro_sanitario TEXT,
            fecha_caducidad TEXT,
            fecha_fabricacion TEXT,

            nombre_generico TEXT,
            nombre_comercial TEXT,
            forma_farmaceutica TEXT,
            concentracion TEXT,
            contenido_neto TEXT,
            via_administracion TEXT,
            requiere_receta INTEGER,

            marca TEXT,
            modelo TEXT,
            condiciones_almacenamiento TEXT,
            advertencias TEXT,

            fabricante TEXT,
            dosis TEXT,
            indicaciones TEXT,
            condiciones_conservacion TEXT,

            foto TEXT,
            stock_actual INTEGER DEFAULT 0
        )
        """)

        # ===== STOCK MOVIMIENTOS =====
        c.execute("""
        CREATE TABLE IF NOT EXISTS stock_movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            insumo_id TEXT NOT NULL,

            tipo TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            stock_resultante INTEGER NOT NULL,

            motivo TEXT,
            referencia TEXT,
            usuario TEXT,

            fecha TEXT NOT NULL,

            FOREIGN KEY(insumo_id) REFERENCES insumos(id)
        )
        """)


# ===== NORMALIZACIÓN =====

def normalize(insumo: dict) -> dict:
    base = {
        "id": "",
        "tipo": "",
        "nombre": "",
        "lote": "",
        "registro_sanitario": "",
        "fecha_caducidad": "",
        "fecha_fabricacion": "",

        "nombre_generico": "",
        "nombre_comercial": "",
        "forma_farmaceutica": "",
        "concentracion": "",
        "contenido_neto": "",
        "via_administracion": "",
        "requiere_receta": 0,

        "marca": "",
        "modelo": "",
        "condiciones_almacenamiento": "",
        "advertencias": "",

        "fabricante": "",
        "dosis": "",
        "indicaciones": "",
        "condiciones_conservacion": "",

        "foto": None,
        "stock_actual": 0
    }
    base.update(insumo)
    base["requiere_receta"] = int(bool(base["requiere_receta"]))
    base["stock_actual"] = int(base.get("stock_actual", 0))
    return base


# ===== CRUD INSUMOS =====

def fetch_all():
    with conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT * FROM insumos ORDER BY id"
        ).fetchall()]


def insert(insumo: dict):
    insumo = normalize(insumo)
    with conn() as c:
        c.execute("""
        INSERT INTO insumos VALUES (
            :id,:tipo,:nombre,:lote,:registro_sanitario,
            :fecha_caducidad,:fecha_fabricacion,
            :nombre_generico,:nombre_comercial,:forma_farmaceutica,
            :concentracion,:contenido_neto,:via_administracion,
            :requiere_receta,
            :marca,:modelo,:condiciones_almacenamiento,:advertencias,
            :fabricante,:dosis,:indicaciones,:condiciones_conservacion,
            :foto,:stock_actual
        )
        """, insumo)


def update(insumo: dict):
    insumo = normalize(insumo)
    with conn() as c:
        c.execute("""
        UPDATE insumos SET
            tipo=:tipo,
            nombre=:nombre,
            lote=:lote,
            registro_sanitario=:registro_sanitario,
            fecha_caducidad=:fecha_caducidad,
            fecha_fabricacion=:fecha_fabricacion,
            nombre_generico=:nombre_generico,
            nombre_comercial=:nombre_comercial,
            forma_farmaceutica=:forma_farmaceutica,
            concentracion=:concentracion,
            contenido_neto=:contenido_neto,
            via_administracion=:via_administracion,
            requiere_receta=:requiere_receta,
            marca=:marca,
            modelo=:modelo,
            condiciones_almacenamiento=:condiciones_almacenamiento,
            advertencias=:advertencias,
            fabricante=:fabricante,
            dosis=:dosis,
            indicaciones=:indicaciones,
            condiciones_conservacion=:condiciones_conservacion,
            foto=:foto,
            stock_actual=:stock_actual
        WHERE id=:id
        """, insumo)


def delete(insumo_id: str):
    with conn() as c:
        c.execute("DELETE FROM insumos WHERE id=?", (insumo_id,))


def next_id(tipo: str) -> int:
    pref = tipo[:3].upper()
    with conn() as c:
        r = c.execute(
            "SELECT id FROM insumos WHERE id LIKE ? ORDER BY id DESC LIMIT 1",
            (f"{pref}-%",)
        ).fetchone()
        return int(r["id"].split("-")[1]) + 1 if r else 1


# ===== STOCK (UNIFICADO) =====

def registrar_stock(
    insumo_id: str,
    cantidad: int,
    tipo: str,
    motivo: str = "",
    referencia: str = "",
    usuario: str = "sistema"
):
    with conn() as c:
        row = c.execute(
            "SELECT stock_actual FROM insumos WHERE id=?",
            (insumo_id,)
        ).fetchone()

        if not row:
            raise ValueError("Insumo no encontrado")

        stock_actual = row["stock_actual"]
        nuevo_stock = stock_actual + cantidad

        if nuevo_stock < 0:
            raise ValueError("Stock insuficiente")

        # actualizar stock
        c.execute(
            "UPDATE insumos SET stock_actual=? WHERE id=?",
            (nuevo_stock, insumo_id)
        )

        # registrar movimiento
        c.execute("""
            INSERT INTO stock_movimientos (
                insumo_id, tipo, cantidad,
                stock_resultante, motivo,
                referencia, usuario, fecha
            ) VALUES (?,?,?,?,?,?,?,?)
        """, (
            insumo_id,
            tipo,
            cantidad,
            nuevo_stock,
            motivo,
            referencia,
            usuario,
            datetime.now().isoformat(timespec="seconds")
        ))


# ===== COMPATIBILIDAD CON CÓDIGO ACTUAL =====

def add_stock(insumo_id: str, cantidad: int, motivo: str):
    registrar_stock(
        insumo_id=insumo_id,
        cantidad=cantidad,
        tipo="ENTRADA" if cantidad > 0 else "SALIDA",
        motivo=motivo
    )
