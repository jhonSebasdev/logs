# Migración de Base de Datos - Log Analyzer

## Cambios Implementados

Se ha actualizado el sistema para incluir información completa de conexión de servidores, incluyendo IP, usuario y contraseña.

### Nuevas Columnas en la tabla `servidores`:

- `ip_servidor` VARCHAR(45) - Dirección IP del servidor
- `usuario_servidor` VARCHAR(100) - Usuario para conectar al servidor  
- `password_servidor` VARCHAR(255) - Contraseña encriptada del servidor
- `puerto` INT(11) - Puerto de conexión (por defecto 22 para SSH)
- `protocolo` ENUM('SSH','FTP','SFTP','SMB','LOCAL') - Protocolo de conexión
- `estado` ENUM('ACTIVO','INACTIVO','ERROR') - Estado de la conexión
- `ultima_conexion` TIMESTAMP - Última conexión exitosa
- `fecha_creacion` TIMESTAMP - Fecha de creación
- `fecha_modificacion` TIMESTAMP - Fecha de modificación

## Instrucciones de Migración

### Opción 1: Nuevo Deployment
```sql
-- Ejecutar el archivo LOGS_UPDATED.sql
SOURCE /path/to/LOGS_UPDATED.sql;
```

### Opción 2: Migración de Base Existente
```sql
-- 1. Hacer backup de la base actual
mysqldump -u username -p log_analyzer > backup_log_analyzer.sql

-- 2. Agregar nuevas columnas
ALTER TABLE servidores 
ADD COLUMN ip_servidor VARCHAR(45) NOT NULL DEFAULT '127.0.0.1' COMMENT 'Dirección IP del servidor',
ADD COLUMN usuario_servidor VARCHAR(100) NOT NULL DEFAULT 'admin' COMMENT 'Usuario para conectar al servidor',
ADD COLUMN password_servidor VARCHAR(255) NOT NULL DEFAULT '' COMMENT 'Contraseña del servidor (encriptada)',
ADD COLUMN puerto INT(11) DEFAULT 22 COMMENT 'Puerto de conexión (SSH por defecto)',
ADD COLUMN protocolo ENUM('SSH','FTP','SFTP','SMB','LOCAL') DEFAULT 'LOCAL' COMMENT 'Protocolo de conexión',
ADD COLUMN estado ENUM('ACTIVO','INACTIVO','ERROR') DEFAULT 'ACTIVO' COMMENT 'Estado de la conexión',
ADD COLUMN ultima_conexion TIMESTAMP NULL DEFAULT NULL COMMENT 'Última vez que se conectó exitosamente',
ADD COLUMN fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha de creación del registro',
ADD COLUMN fecha_modificacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Fecha de última modificación';

-- 3. Crear índices para optimización
CREATE INDEX idx_servidores_ip ON servidores(ip_servidor);
CREATE INDEX idx_servidores_estado ON servidores(estado);
CREATE INDEX idx_servidores_estado_fecha ON servidores(estado, fecha_modificacion);
CREATE INDEX idx_servidores_usuario_estado ON servidores(usuario_id, estado);

-- 4. Actualizar registros existentes con valores por defecto
UPDATE servidores 
SET 
    ip_servidor = '127.0.0.1',
    usuario_servidor = 'admin',
    password_servidor = 'YWRtaW4xMjM=', -- 'admin123' encriptado
    protocolo = 'LOCAL',
    estado = 'ACTIVO'
WHERE ip_servidor = '' OR ip_servidor IS NULL;
```

## Verificación de Migración

```sql
-- Verificar estructura de la tabla
DESCRIBE servidores;

-- Verificar datos migrados
SELECT id, nombre, ip_servidor, usuario_servidor, protocolo, estado 
FROM servidores;

-- Verificar índices
SHOW INDEX FROM servidores;
```

## Características de Seguridad

### Encriptación de Contraseñas
- Las contraseñas se encriptan usando **Fernet encryption** (AES 128)
- Clave derivada con **PBKDF2** (100,000 iteraciones)
- Salt fijo para consistencia (en producción usar salt único por contraseña)

### Validaciones
- **Validación de IP**: Formato IPv4 válido o nombres especiales (localhost, 127.0.0.1)
- **Validación de Puerto**: Rango 1-65535
- **Sanitización de Input**: Prevención de inyecciones de código
- **Campos Requeridos**: Validación de todos los campos obligatorios

### Funciones de Utilidad
```python
from crypto_utils import encrypt_server_password, decrypt_server_password

# Encriptar contraseña
encrypted = encrypt_server_password("mi_contraseña")

# Desencriptar contraseña  
decrypted = decrypt_server_password(encrypted)
```

## Nuevas Dependencias

Agregada a `requirements.txt`:
```
cryptography==41.0.7
```

## Instalación
```bash
pip install cryptography==41.0.7
```

## Notas Importantes

1. **Backup**: Siempre hacer backup antes de la migración
2. **Passwords Existentes**: Se asignarán valores por defecto que deben actualizarse
3. **Producción**: Cambiar la clave maestra de encriptación en `crypto_utils.py`
4. **Variables de Entorno**: Considerar usar variables de entorno para claves sensibles
5. **Logs**: Las operaciones de migración se registran en los logs del sistema