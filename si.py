import sqlite3
from pathlib import Path

def mostrar_datos():
    db_path = Path("data/device_data.db")
    
    if not db_path.exists():
        print("Base de datos no encontrada")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Mostrar estructura de la tabla
    cursor.execute("PRAGMA table_info(device_data)")
    columnas = cursor.fetchall()
    print("Estructura de la tabla:")
    for col in columnas:
        print(f"  {col[1]} ({col[2]})")
    
    print("\n" + "="*80 + "\n")
    
    # Mostrar últimos 10 registros
    cursor.execute("SELECT * FROM device_data ORDER BY timestamp DESC LIMIT 10")
    registros = cursor.fetchall()
    
    print("Últimos 10 registros:")
    print("-" * 80)
    for reg in registros:
        print(f"ID: {reg[0]}, Dispositivo: {reg[1]}, Temp: {reg[2]}, Hum: {reg[4]}, Fecha: {reg[12]}")
    
    print("\n" + "="*80 + "\n")
    
    # Estadísticas
    cursor.execute("SELECT COUNT(*) FROM device_data")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT device_id) FROM device_data")
    dispositivos = cursor.fetchone()[0]
    
    print(f"Estadísticas:")
    print(f"  Total de registros: {total}")
    print(f"  Dispositivos únicos: {dispositivos}")
    
    conn.close()

if __name__ == "__main__":
    mostrar_datos()