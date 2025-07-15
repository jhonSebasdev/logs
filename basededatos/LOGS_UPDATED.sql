-- --------------------------------------------------------
-- Log Analyzer Database Schema - Updated Version
-- --------------------------------------------------------

CREATE DATABASE IF NOT EXISTS `log_analyzer` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;
USE `log_analyzer`;

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS `usuarios` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(50) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Insertar usuario admin
INSERT IGNORE INTO `usuarios` (`id`, `username`, `password`) VALUES
  (1, 'admin', 'admin');

-- Tabla de servidores
CREATE TABLE IF NOT EXISTS `servidores` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `usuario_id` INT(11) NOT NULL,
  `nombre` VARCHAR(100) NOT NULL,
  `ip_servidor` VARCHAR(45) NOT NULL,
  `usuario_servidor` VARCHAR(100) NOT NULL,
  `password_servidor` VARCHAR(255) NOT NULL,
  `ruta_log` TEXT NOT NULL,
  `puerto` INT(11) DEFAULT 22,
  `protocolo` ENUM('SSH','FTP','SFTP','SMB','LOCAL') DEFAULT 'SSH',
  `estado` ENUM('ACTIVO','INACTIVO','ERROR') DEFAULT 'ACTIVO',
  `ultima_conexion` TIMESTAMP NULL DEFAULT NULL,
  `fecha_creacion` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_modificacion` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `usuario_id` (`usuario_id`),
  KEY `ip_servidor` (`ip_servidor`),
  KEY `estado` (`estado`),
  CONSTRAINT `servidores_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Insertar registros iniciales si la tabla está vacía
INSERT IGNORE INTO `servidores` (`usuario_id`, `nombre`, `ip_servidor`, `usuario_servidor`, `password_servidor`, `ruta_log`, `protocolo`)
SELECT 
    1, 'Servidor Local XAMPP - Error Log', '127.0.0.1', 'admin', 'admin123', 'C:\\xampp\\apache\\logs\\error.log', 'LOCAL'
WHERE NOT EXISTS (SELECT 1 FROM `servidores`);

INSERT IGNORE INTO `servidores` (`usuario_id`, `nombre`, `ip_servidor`, `usuario_servidor`, `password_servidor`, `ruta_log`, `protocolo`)
SELECT 
    1, 'Servidor Local XAMPP - Access Log', '127.0.0.1', 'admin', 'admin123', 'C:\\xampp\\apache\\logs\\access.log', 'LOCAL'
WHERE (SELECT COUNT(*) FROM `servidores`) = 1;

-- Crear índices adicionales
-- IMPORTANTE: NO USAR IF NOT EXISTS
-- Verificar antes de ejecutar para evitar errores de duplicado

-- Comprobaciones manuales necesarias si lo corres directamente en producción
