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
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            usuario TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            rol TEXT NOT NULL,
            telefono TEXT,
            email TEXT,
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

        cur = conn.execute("SELECT COUNT(*) FROM users")
        if cur.fetchone()[0] == 0:
            conn.execute("""
            INSERT INTO users (
                id, nombre, apellido, usuario, password, rol,
                estado_documentos, apto_operar
            ) VALUES (
                'USR-001', 'Admin', 'Principal',
                'admin', 'admin123', 'Administrador',
                'Validado', 1
            )
            """)


def validate_login(usuario, password, rol):
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT password, rol FROM users WHERE usuario=?",
            (usuario.strip(),)
        )
        row = cur.fetchone()

        if not row:
            return False

        return (
            row["password"] == password.strip()
            and row["rol"].lower() == rol.lower()
        )


def fetch_all_users():
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM users ORDER BY id")
        return [dict(row) for row in cur.fetchall()]


def get_next_user_id():
    with get_connection() as conn:
        cur = conn.execute("SELECT id FROM users ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        return int(row["id"].split("-")[1]) + 1 if row else 1


def usuario_exists(usuario: str, exclude_id: str | None = None) -> bool:
    with get_connection() as conn:
        if exclude_id:
            cur = conn.execute(
                "SELECT 1 FROM users WHERE usuario=? AND id!=?",
                (usuario.strip(), exclude_id)
            )
        else:
            cur = conn.execute(
                "SELECT 1 FROM users WHERE usuario=?",
                (usuario.strip(),)
            )
        return cur.fetchone() is not None


def insert_user(user: dict):
    if not user.get("password"):
        raise ValueError("La contraseña es obligatoria")

    if usuario_exists(user["usuario"]):
        raise ValueError("El nombre de usuario ya existe")

    try:
        with get_connection() as conn:
            conn.execute("""
            INSERT INTO users (
                id, nombre, apellido, usuario, password, rol,
                telefono, email, rfc, tipo_sangre, alergias,
                enfermedades, notas_medicas, apto_operar,
                foto, ine, licencia, licencia_num, licencia_exp,
                estado_documentos, synced, last_sync
            ) VALUES (
                :id, :nombre, :apellido, :usuario, :password, :rol,
                :telefono, :email, :rfc, :tipo_sangre, :alergias,
                :enfermedades, :notas_medicas, :apto_operar,
                :foto, :ine, :licencia, :licencia_num, :licencia_exp,
                :estado_documentos, :synced, :last_sync
            )
            """, user)

    except sqlite3.IntegrityError as e:
        if "users.usuario" in str(e):
            raise ValueError("El nombre de usuario ya existe")
        raise


def update_user(user: dict):
    if usuario_exists(user["usuario"], exclude_id=user["id"]):
        raise ValueError("El nombre de usuario ya existe")

    try:
        with get_connection() as conn:
            conn.execute("""
            UPDATE users SET
                nombre=:nombre,
                apellido=:apellido,
                usuario=:usuario,
                password=:password,
                rol=:rol,
                telefono=:telefono,
                email=:email,
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

    except sqlite3.IntegrityError as e:
        if "users.usuario" in str(e):
            raise ValueError("El nombre de usuario ya existe")
        raise


def delete_user(user_id: str):
    with get_connection() as conn:
        conn.execute("DELETE FROM users WHERE id=?", (user_id,))
