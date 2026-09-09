from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioLogado
from app.security import decodificar_token

# tokenUrl aponta para a rota de login — usado só para a doc automática (/docs)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def obter_usuario_atual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> UsuarioLogado:
    credenciais_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou sessão expirada",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decodificar_token(token)
    if payload is None:
        raise credenciais_invalidas

    usuario_id = payload.get("sub")
    if usuario_id is None:
        raise credenciais_invalidas

    usuario = db.query(Usuario).filter(Usuario.id == int(usuario_id)).first()
    if usuario is None or not usuario.ativo:
        raise credenciais_invalidas

    if usuario.perfil is None:
        # Não deveria acontecer (perfil_id é validado na criação/edição de usuário),
        # mas se acontecer por dado legado, falhar com uma mensagem clara é melhor
        # que um 500 cru tentando ler .nome de um relacionamento vazio.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário sem perfil válido associado. Contate o administrador.",
        )

    return UsuarioLogado(
        id=usuario.id,
        nome=usuario.nome,
        usuario=usuario.usuario,
        perfil_id=usuario.perfil_id,
        perfil_nome=usuario.perfil.nome,
    )


def exigir_perfis(*perfis_permitidos: str):
    """
    Uso: Depends(exigir_perfis("Administrador"))
    Bloqueia o acesso se o perfil do usuário logado não estiver na lista.
    """

    def verificador(usuario: UsuarioLogado = Depends(obter_usuario_atual)) -> UsuarioLogado:
        if usuario.perfil_nome not in perfis_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Seu perfil ({usuario.perfil_nome}) não tem permissão para esta ação.",
            )
        return usuario

    return verificador
