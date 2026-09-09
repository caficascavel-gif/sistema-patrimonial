from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LoginRequest(BaseModel):
    usuario: str
    senha: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expira_em_minutos: int


class UsuarioBase(BaseModel):
    nome: str
    usuario: str
    perfil_id: int
    secretaria_id: int | None = None
    setor_id: int | None = None
    ativo: bool = True


class UsuarioCreate(UsuarioBase):
    senha: str


class UsuarioUpdate(BaseModel):
    nome: str | None = None
    perfil_id: int | None = None
    secretaria_id: int | None = None
    setor_id: int | None = None
    ativo: bool | None = None
    senha: str | None = None  # se informado, redefine a senha


class UsuarioOut(UsuarioBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    criado_em: datetime


class UsuarioLogado(BaseModel):
    """Retornado dentro do token / usado como identidade do usuário na requisição."""
    id: int
    nome: str
    usuario: str
    perfil_id: int
    perfil_nome: str
