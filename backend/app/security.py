from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.config import settings

# Uso direto da lib bcrypt (em vez de passlib, que tem incompatibilidade conhecida
# com versões recentes do bcrypt — passlib está sem manutenção ativa).


def hash_senha(senha_texto: str) -> str:
    senha_bytes = senha_texto.encode("utf-8")
    hash_bytes = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())
    return hash_bytes.decode("utf-8")


def verificar_senha(senha_texto: str, senha_hash: str) -> bool:
    return bcrypt.checkpw(senha_texto.encode("utf-8"), senha_hash.encode("utf-8"))


def criar_token_acesso(dados: dict) -> str:
    """Gera um JWT. Expira em settings.jwt_expire_minutes (8h por padrão)."""
    payload = dados.copy()
    expira_em = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload.update({"exp": expira_em})
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decodificar_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None
