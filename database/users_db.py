import sqlite3
from pathlib import Path

DB_PATH = Path("data/users.db")


def get_connection():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            nombre TEXT,
            apellido TEXT,
            usuario TEXT,
            telefono TEXT,
            email TEXT,
            rol TEXT,
            rfc TEXT,
            tipo_sangre TEXT,
            alergias TEXT,
            enfermedades TEXT,
            notas_medicas TEXT,
            apto_operar INTEGER,
            foto TEXT,
            ine TEXT,
            licencia TEXT,
            licencia_num TEXT,
            licencia_exp TEXT,
            estado_documentos TEXT,
            synced INTEGER DEFAULT 0,
            last_sync TEXT
        )
        """)


def fetch_all_users():
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM users ORDER BY id")
        return [dict(row) for row in cur.fetchall()]


def get_next_user_id():
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT id FROM users ORDER BY id DESC LIMIT 1"
        )
        row = cur.fetchone()

    if not row:
        return 1

    return int(row["id"].split("-")[1]) + 1


def insert_user(user: dict):
    with get_connection() as conn:
        conn.execute("""
        INSERT INTO users (
            id, nombre, apellido, usuario, telefono, email, rol,
            rfc, tipo_sangre, alergias, enfermedades, notas_medicas,
            apto_operar, foto, ine, licencia, licencia_num,
            licencia_exp, estado_documentos, synced, last_sync
        ) VALUES (
            :id, :nombre, :apellido, :usuario, :telefono, :email, :rol,
            :rfc, :tipo_sangre, :alergias, :enfermedades, :notas_medicas,
            :apto_operar, :foto, :ine, :licencia, :licencia_num,
            :licencia_exp, :estado_documentos, :synced, :last_sync
        )
        """, user)


def update_user(user: dict):
    with get_connection() as conn:
        conn.execute("""
        UPDATE users SET
            nombre=:nombre,
            apellido=:apellido,
            usuario=:usuario,
            telefono=:telefono,
            email=:email,
            rol=:rol,
            rfc=:rfc,
            tipo_sangre=:tipo_sangre,
            alergias=:alergias,
            enfermedades=:enfermedades,
            notas_medicas=:notas_medicas,
            apto_operar=:apto_operar,
            foto=:foto,
            ine=:ine,
            licencia=:licencia,
            licencia_num=:licencia_num,
            licencia_exp=:licencia_exp,
            estado_documentos=:estado_documentos,
            synced=:synced,
            last_sync=:last_sync
        WHERE id=:id
        """, user)


def delete_user(user_id: str):
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM users WHERE id=?",
            (user_id,)
        )
