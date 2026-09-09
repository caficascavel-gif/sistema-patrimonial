from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import LoginRequest, TokenResponse
from app.security import criar_token_acesso, verificar_senha

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=TokenResponse)
def login(dados: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.usuario == dados.usuario).first()

    # Mensagem genérica de propósito: não revelar se foi o usuário ou a senha que errou
    erro_login = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Usuário ou senha inválidos.",
    )

    if usuario is None or not verificar_senha(dados.senha, usuario.senha_hash):
        raise erro_login

    if not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo. Procure o administrador do sistema.",
        )

    token = criar_token_acesso({"sub": str(usuario.id)})

    return TokenResponse(access_token=token, expira_em_minutos=settings.jwt_expire_minutes)
