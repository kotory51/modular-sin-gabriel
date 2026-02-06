from datetime import datetime
from database.insumos_db import conn


def registrar_movimiento(
    insumo_id: str,
    cantidad: int,
    tipo: str,
    motivo: str = "",
    referencia: str = "",
    usuario: str = "sistema"
):
    with conn() as c:
        cur = c.execute(
            "SELECT stock_actual FROM insumos WHERE id=?",
            (insumo_id,)
        ).fetchone()

        if not cur:
            raise ValueError("Insumo no encontrado")

        stock_actual = cur["stock_actual"]
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
            insumo_id, tipo, cantidad,
            nuevo_stock, motivo,
            referencia, usuario,
            datetime.now().isoformat(timespec="seconds")
        ))
