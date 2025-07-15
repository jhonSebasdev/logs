from flask import Flask, render_template, request, redirect, url_for, session, send_file
from db import conectar
import os
from flask import request
import mysql.connector
import importlib.util
from flask import jsonify
import paramiko
import stat
from crypto_utils import encrypt_server_password, decrypt_server_password, validate_ip_address, sanitize_input
import io

app = Flask(__name__)
app.secret_key = 'clave123'  

# Ruta raíz redirecciona al health check
@app.route('/')
def home():
    return redirect('/health')

@app.route('/subir_log', methods=['POST'])
def subir_log():
    archivo = request.files['archivo']
    if archivo:
        ruta = os.path.join('uploads', archivo.filename)
        archivo.save(ruta)
        return redirect(url_for('ver_log', ruta_log=ruta))
    
def leer_log_remoto(ip, user, password, ruta_log):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username=user, password=password)
    
    sftp = ssh.open_sftp()
    with sftp.file(ruta_log, 'r') as f:
        lineas = f.readlines()
    
    sftp.close()
    ssh.close()
    return lineas    

# Health Check - Verificación del sistema
@app.route('/health')
def health_check():
    # Verificar conexión a base de datos
    db_status = check_database_connection()
    
    # Verificar tablas
    tables_status = check_database_tables()
    
    # Verificar archivos de ML
    ml_status = check_ml_files()
    
    # Verificar directorio de logs
    logs_status = check_logs_directory()
    
    # Verificar dependencias
    dependencies_status = check_dependencies()
    
    # Determinar si el sistema está listo
    system_ready = (db_status['connected'] and 
                   tables_status['all_exist'] and 
                   dependencies_status['all_installed'])
    
    return render_template('health_check.html',
                         db_status=db_status,
                         tables_status=tables_status,
                         ml_status=ml_status,
                         logs_status=logs_status,
                         dependencies_status=dependencies_status,
                         system_ready=system_ready)

def conectar():
    return mysql.connector.connect(
        host="mysql",
        user="appuser",
        password="apppassword",
        database="log_analyzer"
    )

def check_database_connection():
    try:
        conn = conectar()
        if conn:
            conn.close()
            return {
                'connected': True,
                'host': 'localhost',
                'database': 'log_analyzer',
                'error': None
            }
        else:
            return {
                'connected': False,
                'host': 'localhost',
                'database': 'log_analyzer',
                'error': 'No se pudo conectar'
            }
    except Exception as e:
        return {
            'connected': False,
            'host': 'localhost',
            'database': 'log_analyzer',
            'error': str(e)
        }

def check_database_tables():
    required_tables = ['usuarios', 'servidores']
    found_tables = []
    
    try:
        conn = conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            found_tables = [table for table in required_tables if table in tables]
            conn.close()
    except Exception:
        pass
    
    missing_tables = [table for table in required_tables if table not in found_tables]
    
    return {
        'all_exist': len(missing_tables) == 0,
        'some_exist': len(found_tables) > 0,
        'found': found_tables,
        'missing': missing_tables
    }

def check_ml_files():
    model_path = 'modelo/modelo.pkl'
    vectorizer_path = 'modelo/vectorizer.pkl'
    data_path = 'modelo/errores.csv'
    
    return {
        'model_exists': os.path.exists(model_path),
        'vectorizer_exists': os.path.exists(vectorizer_path),
        'data_exists': os.path.exists(data_path),
        'ready': os.path.exists(model_path) and os.path.exists(vectorizer_path)
    }

def check_logs_directory():
    logs_path = 'logs'
    
    try:
        if os.path.exists(logs_path):
            files = os.listdir(logs_path)
            return {
                'accessible': True,
                'path': logs_path,
                'file_count': len(files)
            }
        else:
            return {
                'accessible': False,
                'path': logs_path,
                'file_count': 0
            }
    except Exception:
        return {
            'accessible': False,
            'path': logs_path,
            'file_count': 0
        }

def check_dependencies():
    required_packages = ['flask', 'mysql.connector', 'sklearn', 'pandas', 'numpy']
    installed = []
    missing = []
    
    for package in required_packages:
        try:
            if package == 'mysql.connector':
                import mysql.connector
                installed.append('mysql-connector-python')
            elif package == 'sklearn':
                import sklearn
                installed.append('scikit-learn')
            else:
                __import__(package)
                installed.append(package)
        except ImportError:
            missing.append(package)
    
    return {
        'all_installed': len(missing) == 0,
        'installed': installed,
        'missing': missing
    }

# Inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        clave = request.form['clave']

        conn = conectar()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE username = %s AND password = %s", (usuario, clave))
            user = cursor.fetchone()
            conn.close()

            if user:
                session['usuario_id'] = user['id']
                session['username'] = user['username']
                return redirect('/dashboard')
            else:
                return render_template('login.html', error="Credenciales incorrectas")
        else:
            return render_template('login.html', error="Error de conexión con la base de datos")

    return render_template('login.html')

# Cierre de sesión
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# Panel principal
@app.route('/dashboard')
def dashboard():
    if 'usuario_id' not in session:
        return redirect('/login')

    conn = conectar()
    servidores = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM servidores WHERE usuario_id = %s", (session['usuario_id'],))
        servidores = cursor.fetchall()
        conn.close()

    return render_template('dashboard.html', servidores=servidores)

# Agregar servidor
@app.route('/add_server', methods=['POST'])
def add_server():
    if 'usuario_id' not in session:
        return redirect('/login')

    # Debug: Imprimir datos recibidos
    print("=== DEBUG ADD SERVER ===")
    print("Form data:", dict(request.form))
    
    # Obtener datos del formulario
    nombre = request.form.get('nombre', '').strip()
    ip_servidor = request.form.get('ip_servidor', '').strip()
    usuario_servidor = request.form.get('usuario_servidor', '').strip()
    password_servidor = request.form.get('password_servidor', '').strip()
    puerto = request.form.get('puerto', '22').strip()
    protocolo = request.form.get('protocolo', 'SSH').strip()
    ruta_log = request.form.get('ruta_log', '').strip()

    print(f"Datos extraídos:")
    print(f"  nombre: '{nombre}'")
    print(f"  ip_servidor: '{ip_servidor}'")
    print(f"  usuario_servidor: '{usuario_servidor}'")
    print(f"  password_servidor: '[OCULTA]'")
    print(f"  puerto: '{puerto}'")
    print(f"  protocolo: '{protocolo}'")
    print(f"  ruta_log: '{ruta_log}'")

    # Validaciones básicas
    if not nombre:
        print("ERROR: Nombre vacío")
        return redirect('/dashboard?error=nombre_requerido')
    
    if not ruta_log:
        print("ERROR: Ruta log vacía")
        return redirect('/dashboard?error=ruta_requerida')

    # Valores por defecto para campos opcionales
    if not ip_servidor:
        ip_servidor = '127.0.0.1'
    if not usuario_servidor:
        usuario_servidor = 'admin'
    if not password_servidor:
        password_servidor = 'admin123'
    if not puerto:
        puerto = '22'

    # Convertir puerto a entero
    try:
        puerto_int = int(puerto)
        if puerto_int < 1 or puerto_int > 65535:
            puerto_int = 22
    except ValueError:
        puerto_int = 22

    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Primero verificar si la tabla tiene las nuevas columnas
            cursor.execute("DESCRIBE servidores")
            columns = [row[0] for row in cursor.fetchall()]
            print(f"Columnas disponibles en la tabla: {columns}")
            
            if 'ip_servidor' in columns and 'usuario_servidor' in columns:
                # Tabla actualizada - usar encriptación
                print("Usando tabla actualizada con encriptación")
                try:
                    encrypted_password = encrypt_server_password(password_servidor)
                    cursor.execute("""
                        INSERT INTO servidores 
                        (usuario_id, nombre, ip_servidor, usuario_servidor, password_servidor, puerto, protocolo, ruta_log, estado) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (session['usuario_id'], nombre, ip_servidor, usuario_servidor, encrypted_password, puerto_int, protocolo, ruta_log, 'ACTIVO'))
                except Exception as e:
                    print(f"Error con encriptación: {e}")
                    # Fallback sin encriptación
                    cursor.execute("""
                        INSERT INTO servidores 
                        (usuario_id, nombre, ip_servidor, usuario_servidor, password_servidor, puerto, protocolo, ruta_log, estado) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (session['usuario_id'], nombre, ip_servidor, usuario_servidor, password_servidor, puerto_int, protocolo, ruta_log, 'ACTIVO'))
            else:
                # Tabla original - solo nombre y ruta
                print("Usando tabla original")
                cursor.execute("""
                    INSERT INTO servidores (usuario_id, nombre, ruta_log) 
                    VALUES (%s, %s, %s)
                """, (session['usuario_id'], nombre, ruta_log))
            
            conn.commit()
            print("Datos guardados exitosamente")
            
        except mysql.connector.Error as e:
            print(f"Error de base de datos: {e}")
            return redirect('/dashboard?error=error_base_datos')
        except Exception as e:
            print(f"Error general: {e}")
            return redirect('/dashboard?error=error_general')
        finally:
            conn.close()
    else:
        print("ERROR: No se pudo conectar a la base de datos")
        return redirect('/dashboard?error=sin_conexion')

    print("Redirigiendo a dashboard")
    return redirect('/dashboard')

@app.route('/editar_log/<int:servidor_id>', methods=['GET', 'POST'])
def editar_log(servidor_id):
    if 'usuario_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        # Obtener y sanitizar datos del formulario
        nombre = sanitize_input(request.form.get('nombre', ''))
        ip_servidor = sanitize_input(request.form.get('ip_servidor', ''))
        usuario_servidor = sanitize_input(request.form.get('usuario_servidor', ''))
        password_servidor = request.form.get('password_servidor', '')
        puerto = request.form.get('puerto', 22)
        protocolo = request.form.get('protocolo', 'SSH')
        estado = request.form.get('estado', 'ACTIVO')
        ruta_log = sanitize_input(request.form.get('ruta_log', ''))

        # Validaciones
        if not all([nombre, ip_servidor, usuario_servidor, ruta_log]):
            return redirect(f'/editar_log/{servidor_id}?error=campos_requeridos')
        
        if not validate_ip_address(ip_servidor):
            return redirect(f'/editar_log/{servidor_id}?error=ip_invalida')

        try:
            puerto = int(puerto)
            if puerto < 1 or puerto > 65535:
                return redirect(f'/editar_log/{servidor_id}?error=puerto_invalido')
        except ValueError:
            return redirect(f'/editar_log/{servidor_id}?error=puerto_invalido')

        conn = conectar()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Si se proporciona nueva contraseña, encriptarla
                if password_servidor:
                    encrypted_password = encrypt_server_password(password_servidor)
                    cursor.execute("""
                        UPDATE servidores 
                        SET nombre = %s, ip_servidor = %s, usuario_servidor = %s, password_servidor = %s, 
                            puerto = %s, protocolo = %s, estado = %s, ruta_log = %s, fecha_modificacion = NOW()
                        WHERE id = %s AND usuario_id = %s
                    """, (nombre, ip_servidor, usuario_servidor, encrypted_password, puerto, protocolo, estado, ruta_log, servidor_id, session['usuario_id']))
                else:
                    # Mantener contraseña existente
                    cursor.execute("""
                        UPDATE servidores 
                        SET nombre = %s, ip_servidor = %s, usuario_servidor = %s, puerto = %s, 
                            protocolo = %s, estado = %s, ruta_log = %s, fecha_modificacion = NOW()
                        WHERE id = %s AND usuario_id = %s
                    """, (nombre, ip_servidor, usuario_servidor, puerto, protocolo, estado, ruta_log, servidor_id, session['usuario_id']))
                
                conn.commit()
            except mysql.connector.Error as e:
                return redirect(f'/editar_log/{servidor_id}?error=error_base_datos')
            except Exception as e:
                return redirect(f'/editar_log/{servidor_id}?error=error_encriptacion')
            finally:
                conn.close()

        return redirect('/dashboard')

    # En caso de GET, mostrar el formulario de edición
    conn = conectar()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM servidores WHERE id = %s AND usuario_id = %s", (servidor_id, session['usuario_id']))
        servidor = cursor.fetchone()
        conn.close()

        if not servidor:
            return "Servidor no encontrado o acceso denegado", 403

        return render_template("editar_log.html", servidor=servidor)
    
    return redirect('/dashboard')

@app.route('/analizar/<int:id_servidor>')
def analizar_log(id_servidor):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT ruta_log, protocolo FROM servidores WHERE id = %s", (id_servidor,))
    resultado = cursor.fetchone()

    if not resultado:
        return "Servidor no encontrado", 404

    ruta_log, protocolo = resultado

    if protocolo != "LOCAL":
        return "Este análisis solo está disponible para archivos locales", 400

    if not os.path.exists(ruta_log):
        return f"Archivo no encontrado: {ruta_log}", 404

    try:
        with open(ruta_log, 'r', encoding='utf-8', errors='ignore') as archivo:
            lineas = archivo.readlines()[-30:]

        return render_template("ver_log.html", lineas=lineas, ruta=ruta_log)
    except Exception as e:
        return f"Error al leer el log: {str(e)}", 500
    


# Ver logs de un servidor
@app.route('/ver_log/<int:servidor_id>')
def ver_log(servidor_id):
    if 'usuario_id' not in session:
        return redirect('/login')

    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM servidores WHERE id = %s AND usuario_id = %s", (servidor_id, session['usuario_id']))
    servidor = cursor.fetchone()
    conn.close()

    if not servidor:
        return "Servidor no encontrado o acceso no autorizado", 403

    try:
        if servidor.get('protocolo', 'LOCAL').upper() in ['SSH', 'SFTP']:
            # Leer archivo remoto por SFTP
            import paramiko
            from crypto_utils import decrypt_server_password
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # Desencriptar la contraseña antes de usarla
            password = servidor['password_servidor']
            try:
                password = decrypt_server_password(password)
            except Exception:
                pass  # Si falla, usar la original (por compatibilidad)
            ssh.connect(
                servidor['ip_servidor'],
                port=int(servidor.get('puerto', 22)),
                username=servidor['usuario_servidor'],
                password=password,
                timeout=5
            )
            sftp = ssh.open_sftp()
            try:
                with sftp.file(servidor['ruta_log'], 'r') as f:
                    lineas = f.readlines()[-30:]
            finally:
                sftp.close()
                ssh.close()
        else:
            # Leer archivo local
            with open(servidor['ruta_log'], 'r', encoding='utf-8', errors='ignore') as f:
                lineas = f.readlines()[-30:]
    except Exception as e:
        lineas = [f"❌ Error al leer el archivo: {e}"]

    return render_template('ver_log.html', servidor=servidor, ruta=servidor['ruta_log'], lineas=lineas)


# Gestión de usuarios
@app.route('/users')
def users():
    if 'usuario_id' not in session:
        return redirect('/login')
    
    conn = conectar()
    usuarios = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username FROM usuarios")
        usuarios = cursor.fetchall()
        # Para cada usuario, obtener los servidores asociados
        for usuario in usuarios:
            cursor.execute("SELECT nombre FROM servidores WHERE usuario_id = %s", (usuario['id'],))
            servidores = [row['nombre'] for row in cursor.fetchall()]
            usuario['servidores'] = servidores
        conn.close()
    
    return render_template('users.html', usuarios=usuarios)

# Crear usuario
@app.route('/create_user', methods=['POST'])
def create_user():
    if 'usuario_id' not in session:
        return redirect('/login')
    
    username = sanitize_input(request.form.get('username', '').strip())
    password = sanitize_input(request.form.get('password', '').strip())
    confirm_password = sanitize_input(request.form.get('confirm_password', '').strip())
    
    if not username or not password:
        return render_template('users.html', error="Usuario y contraseña son requeridos")
    
    if password != confirm_password:
        return render_template('users.html', error="Las contraseñas no coinciden")
    
    if len(password) < 4:
        return render_template('users.html', error="La contraseña debe tener al menos 4 caracteres")
    
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE username = %s", (username,))
            if cursor.fetchone()[0] > 0:
                conn.close()
                return render_template('users.html', error="El usuario ya existe")
            
            cursor.execute("INSERT INTO usuarios (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            conn.close()
            return redirect('/users?success=Usuario creado exitosamente')
        except mysql.connector.Error as e:
            conn.close()
            return render_template('users.html', error=f"Error al crear usuario: {str(e)}")
    else:
        return render_template('users.html', error="Error de conexión con la base de datos")
    
@app.route('/eliminar/<int:servidor_id>', methods=['POST'])
def eliminar_log(servidor_id):
    conn = conectar()
    if not conn:
        return "Error de conexión", 500

    cursor = conn.cursor()
    cursor.execute("DELETE FROM servidores WHERE id = %s", (servidor_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('dashboard'))    

@app.route("/probar_conexion", methods=["POST"])
def probar_conexion():
    try:
        data = request.get_json()
        ip = data.get("ip", "127.0.0.1")
        usuario = data.get("usuario", "root")
        password = data.get("password", "")
        protocolo = data.get("protocolo", "SSH")
        puerto = int(data.get("puerto", 22))

        if protocolo == "LOCAL":
            return jsonify({"ok": True, "mensaje": "Conexión local simulada exitosa"})

        # Intentar conexión SSH/SFTP
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(ip, port=puerto, username=usuario, password=password, timeout=5)
            # Probar SFTP
            try:
                sftp = ssh.open_sftp()
                sftp.close()
                ssh.close()
                return jsonify({"ok": True, "mensaje": "Conexión SSH/SFTP exitosa"})
            except Exception as sftp_error:
                ssh.close()
                return jsonify({"ok": False, "mensaje": f"Conexión SSH exitosa, pero SFTP falló: {str(sftp_error)}"}), 500
        except Exception as ssh_error:
            return jsonify({"ok": False, "mensaje": f"Error de conexión SSH: {str(ssh_error)}"}), 500
    except Exception as e:
        return jsonify({"ok": False, "mensaje": f"Error inesperado: {str(e)}"}), 500

@app.route('/listar_archivos', methods=['POST'])
def listar_archivos():
    try:
        data = request.get_json()
        ip = data.get('ip', '127.0.0.1')
        usuario = data.get('usuario', 'root')
        password = data.get('password', '')
        puerto = int(data.get('puerto', 22))
        ruta = data.get('ruta', '/var/log')
        protocolo = data.get('protocolo', 'SSH')

        if protocolo == 'LOCAL':
            # Listar archivos locales
            try:
                archivos = []
                for nombre in os.listdir(ruta):
                    path = os.path.join(ruta, nombre)
                    archivos.append({
                        'nombre': nombre,
                        'es_directorio': os.path.isdir(path)
                    })
                return jsonify({'ok': True, 'archivos': archivos})
            except Exception as e:
                return jsonify({'ok': False, 'mensaje': f'Error local: {str(e)}'}), 500

        # Listar archivos por SFTP
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port=puerto, username=usuario, password=password, timeout=5)
        sftp = ssh.open_sftp()
        archivos = []
        for entry in sftp.listdir_attr(ruta):
            archivos.append({
                'nombre': entry.filename,
                'es_directorio': stat.S_ISDIR(entry.st_mode)
            })
        sftp.close()
        ssh.close()
        return jsonify({'ok': True, 'archivos': archivos})
    except Exception as e:
        return jsonify({'ok': False, 'mensaje': f'Error al listar archivos: {str(e)}'}), 500

# Eliminar usuario
@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if 'usuario_id' not in session:
        
        return redirect('/login')
    
    if user_id == session['usuario_id']:
        return redirect('/users?error=No puedes eliminar tu propio usuario')
    
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM usuarios WHERE id = %s", (user_id,))
            conn.commit()
            conn.close()
            return redirect('/users?success=Usuario eliminado exitosamente')
        except mysql.connector.Error as e:
            conn.close()
            return redirect('/users?error=Error al eliminar usuario')
    else:
        return redirect('/users?error=Error de conexión con la base de datos')

@app.route('/descargar_log/<int:servidor_id>')
def descargar_log(servidor_id):
    if 'usuario_id' not in session:
        return redirect('/login')

    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM servidores WHERE id = %s AND usuario_id = %s", (servidor_id, session['usuario_id']))
    servidor = cursor.fetchone()
    conn.close()

    if not servidor:
        return "Servidor no encontrado o acceso no autorizado", 403

    try:
        filename = servidor['ruta_log'].split('/')[-1] or 'log.txt'
        if servidor.get('protocolo', 'LOCAL').upper() in ['SSH', 'SFTP']:
            import paramiko
            from crypto_utils import decrypt_server_password
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            password = servidor['password_servidor']
            try:
                password = decrypt_server_password(password)
            except Exception:
                pass
            ssh.connect(
                servidor['ip_servidor'],
                port=int(servidor.get('puerto', 22)),
                username=servidor['usuario_servidor'],
                password=password,
                timeout=5
            )
            sftp = ssh.open_sftp()
            try:
                with sftp.file(servidor['ruta_log'], 'r') as f:
                    contenido = f.read()
                file_obj = io.BytesIO(contenido if isinstance(contenido, bytes) else contenido.encode('utf-8'))
            finally:
                sftp.close()
                ssh.close()
        else:
            with open(servidor['ruta_log'], 'rb') as f:
                file_obj = io.BytesIO(f.read())
        file_obj.seek(0)
        return send_file(file_obj, as_attachment=True, download_name=filename)
    except Exception as e:
        return f"Error al descargar el log: {e}", 500

@app.route('/reportes')
def reportes():
    if 'usuario_id' not in session:
        return redirect('/login')
    return render_template('reportes.html')

@app.route('/configuracion')
def configuracion():
    if 'usuario_id' not in session:
        return redirect('/login')
    return render_template('configuracion.html')

# Ejecutar servidor Flask
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
    
