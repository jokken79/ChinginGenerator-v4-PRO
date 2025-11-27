#!/usr/bin/env python3
"""
Módulo de Autenticación para 賃金台帳 Generator v4 PRO
Implementa HTTP Basic + JWT tokens para seguridad
"""

from datetime import datetime, timedelta
from typing import Optional
import jwt
import secrets
from passlib.context import CryptContext
from fastapi import HTTPException, Security, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import sqlite3
import os

# Configuración
SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Contexto para hashing de passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Basic Security
security = HTTPBasic()

class AuthManager:
    """Gestiona autenticación y autorización"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica password contra hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Genera hash de password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Crea JWT token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verifica y decodifica JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return payload
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[dict]:
        """Autentica usuario contra base de datos"""
        try:
            with sqlite3.connect('chingin_data.db') as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute(
                    "SELECT * FROM users WHERE username = ? AND is_active = 1",
                    (username,)
                )
                user = cursor.fetchone()
                
                if user and AuthManager.verify_password(password, user['password_hash']):
                    return dict(user)
                return None
        except Exception:
            # Si tabla users no existe, crear usuario admin por defecto
            if username == "admin" and password == "admin123":
                return {"username": "admin", "role": "admin", "is_active": True}
            return None

# Dependencias de FastAPI
async def get_current_user(credentials: HTTPBasicCredentials = Security(security)):
    """Obtiene usuario actual via HTTP Basic"""
    user = AuthManager.authenticate_user(credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user

async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    """Verifica que usuario esté activo"""
    if not current_user.get("is_active", True):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Roles
def require_admin(current_user: dict = Depends(get_current_active_user)):
    """Requiere rol de administrador"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

def init_auth_db():
    """Inicializa tabla de usuarios si no existe"""
    try:
        with sqlite3.connect('chingin_data.db') as conn:
            cursor = conn.cursor()
            
            # Crear tabla users
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    failed_login_attempts INTEGER DEFAULT 0,
                    locked_until TIMESTAMP
                )
            ''')
            
            # Crear usuario admin por defecto si no existe
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
            if cursor.fetchone()[0] == 0:
                admin_hash = AuthManager.get_password_hash("admin123")
                cursor.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                    ("admin", admin_hash, "admin")
                )
                print("✅ Usuario admin creado (admin/admin123)")
            
            conn.commit()
    except Exception as e:
        print(f"❌ Error inicializando auth: {e}")

if __name__ == "__main__":
    init_auth_db()