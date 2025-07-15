import mysql.connector
import os

def conectar():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'mysql'),
            user=os.getenv('DB_USER', 'appuser'),
            password=os.getenv('DB_PASSWORD', 'apppassword'),
            database=os.getenv('DB_NAME', 'log_analyzer'),
            port=3306
        )
        return connection
    except mysql.connector.Error as error:
        print(f"Error al conectar a MySQL: {error}")
        return None

def obtener_servidores():
    conn = conectar()
    if not conn:
        return []

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM servidores")
    servidores = cursor.fetchall()
    conn.close()
    return servidores

def obtener_servidor_por_id(servidor_id):
    conn = conectar()
    if not conn:
        return None

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM servidores WHERE id = %s", (servidor_id,))
    servidor = cursor.fetchone()
    conn.close()
    return servidor
