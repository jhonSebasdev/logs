"""
Utilidades de seguridad y encriptación para el Log Analyzer
Manejo seguro de contraseñas y datos sensibles
"""

import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

class PasswordManager:
    """Gestión segura de contraseñas usando Fernet encryption"""
    
    def __init__(self, master_key: str = None):
        """
        Inicializa el gestor de contraseñas
        Args:
            master_key: Clave maestra para encriptación. Si no se proporciona, usa una por defecto
        """
        if master_key is None:
            # En producción, esto debería estar en variables de entorno
            master_key = "log_analyzer_master_key_2024_secure"
        
        self.master_key = master_key.encode()
        self._cipher = self._create_cipher()
    
    def _create_cipher(self):
        """Crea el objeto cipher para encriptación/desencriptación"""
        # Generar salt fijo (en producción debería ser aleatorio por contraseña)
        salt = b'log_analyzer_salt_2024_fixed'
        
        # Derivar clave usando PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key))
        return Fernet(key)
    
    def encrypt_password(self, password: str) -> str:
        """
        Encripta una contraseña
        Args:
            password: Contraseña en texto plano
        Returns:
            Contraseña encriptada en base64
        """
        try:
            encrypted_bytes = self._cipher.encrypt(password.encode())
            return base64.urlsafe_b64encode(encrypted_bytes).decode()
        except Exception as e:
            raise Exception(f"Error encriptando contraseña: {str(e)}")
    
    def decrypt_password(self, encrypted_password: str) -> str:
        """
        Desencripta una contraseña
        Args:
            encrypted_password: Contraseña encriptada en base64
        Returns:
            Contraseña en texto plano
        """
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_password.encode())
            decrypted_bytes = self._cipher.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
        except Exception as e:
            raise Exception(f"Error desencriptando contraseña: {str(e)}")
    
    def hash_password(self, password: str) -> str:
        """
        Genera un hash de la contraseña usando SHA256
        Útil para verificación sin almacenar la contraseña real
        Args:
            password: Contraseña en texto plano
        Returns:
            Hash SHA256 en hexadecimal
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """
        Verifica si una contraseña coincide con su hash
        Args:
            password: Contraseña en texto plano
            hashed: Hash almacenado
        Returns:
            True si coinciden, False en caso contrario
        """
        return self.hash_password(password) == hashed

def mask_password(password: str, show_chars: int = 3) -> str:
    """
    Enmascara una contraseña para mostrar de forma segura
    Args:
        password: Contraseña a enmascarar
        show_chars: Número de caracteres a mostrar al final
    Returns:
        Contraseña enmascarada
    """
    if len(password) <= show_chars:
        return "*" * len(password)
    
    return "*" * (len(password) - show_chars) + password[-show_chars:]

def generate_secure_key() -> str:
    """
    Genera una clave segura aleatoria
    Returns:
        Clave segura en base64
    """
    return base64.urlsafe_b64encode(os.urandom(32)).decode()

def validate_ip_address(ip: str) -> bool:
    """
    Valida si una dirección IP es válida
    Args:
        ip: Dirección IP a validar
    Returns:
        True si es válida, False en caso contrario
    """
    try:
        import ipaddress
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        # Permitir nombres especiales
        allowed_names = ['localhost', '127.0.0.1', '0.0.0.0']
        return ip.lower() in allowed_names

def sanitize_input(input_str: str) -> str:
    """
    Sanitiza input del usuario para prevenir inyecciones
    Args:
        input_str: String a sanitizar
    Returns:
        String sanitizado
    """
    if not input_str:
        return ""
    
    # Remover caracteres peligrosos
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '`', '|', '$']
    sanitized = input_str
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    return sanitized.strip()

# Instancia global del gestor de contraseñas
password_manager = PasswordManager()

# Funciones de conveniencia
def encrypt_server_password(password: str) -> str:
    """Encripta una contraseña de servidor"""
    return password_manager.encrypt_password(password)

def decrypt_server_password(encrypted_password: str) -> str:
    """Desencripta una contraseña de servidor"""
    return password_manager.decrypt_password(encrypted_password)

def mask_server_password(password: str) -> str:
    """Enmascara una contraseña de servidor para mostrar"""
    return mask_password(password)