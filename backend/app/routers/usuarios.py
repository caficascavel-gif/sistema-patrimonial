from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.models import Perfil, Secretaria, Setor
from app.schemas.usuario import UsuarioCreate, UsuarioOut, UsuarioUpdate, UsuarioLogado
from app.security import hash_senha
from app.utils.permissoes import exigir_perfis, obter_usuario_atual

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


def _validar_fks_usuario(db: Session, dados: dict):
    """
    Valida perfil/secretaria/setor antes de gravar. Um perfil_id inválido é
    especialmente perigoso aqui: sem essa checagem, o usuário fica gravado mas
    o login dele quebra depois com um 500 genérico (usuario.perfil.nome em
    cima de um relacionamento vazio), em vez de um erro claro na hora de criar.
    """
    if dados.get("perfil_id") and not db.query(Perfil).filter(Perfil.id == dados["perfil_id"]).first():
        raise HTTPException(status_code=400, detail="Perfil informado não existe.")
    if dados.get("secretaria_id") and not db.query(Secretaria).filter(Secretaria.id == dados["secretaria_id"]).first():
        raise HTTPException(status_code=400, detail="Secretaria informada não existe.")
    if dados.get("setor_id") and not db.query(Setor).filter(Setor.id == dados["setor_id"]).first():
        raise HTTPException(status_code=400, detail="Setor informado não existe.")


@router.get("/me", response_model=UsuarioLogado)
def meu_usuario(usuario: UsuarioLogado = Depends(obter_usuario_atual)):
    """Qualquer usuário autenticado pode consultar seus próprios dados."""
    return usuario


@router.get("", response_model=list[UsuarioOut])
def listar_usuarios(
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(exigir_perfis("Administrador")),
):
    return db.query(Usuario).order_by(Usuario.nome).all()


@router.post("", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def criar_usuario(
    dados: UsuarioCreate,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(exigir_perfis("Administrador")),
):
    ja_existe = db.query(Usuario).filter(Usuario.usuario == dados.usuario).first()
    if ja_existe:
        raise HTTPException(status_code=400, detail="Já existe um usuário com esse login.")

    _validar_fks_usuario(db, dados.model_dump())

    novo = Usuario(
        nome=dados.nome,
        usuario=dados.usuario,
        senha_hash=hash_senha(dados.senha),
        perfil_id=dados.perfil_id,
        secretaria_id=dados.secretaria_id,
        setor_id=dados.setor_id,
        ativo=dados.ativo,
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@router.put("/{usuario_id}", response_model=UsuarioOut)
def atualizar_usuario(
    usuario_id: int,
    dados: UsuarioUpdate,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(exigir_perfis("Administrador")),
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    dados_alterados = dados.model_dump(exclude_unset=True)
    if "senha" in dados_alterados:
        senha_nova = dados_alterados.pop("senha")
        if senha_nova:
            usuario.senha_hash = hash_senha(senha_nova)

    _validar_fks_usuario(db, dados_alterados)

    for campo, valor in dados_alterados.items():
        setattr(usuario, campo, valor)

    db.commit()
    db.refresh(usuario)
    return usuario
