import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.database import get_db
from app.models import Documento, Patrimonio
from app.schemas.documento import DocumentoOut, TIPOS_DOCUMENTO
from app.schemas.usuario import UsuarioLogado
from app.utils.permissoes import exigir_perfis, obter_usuario_atual

PERFIS_QUE_ANEXAM = ("Administrador", "Patrimônio", "Administrativo/Compras", "Engenharia Clínica")

router = APIRouter(prefix="/patrimonios/{patrimonio_id}/documentos", tags=["Documentos"])


def _pasta_do_patrimonio(patrimonio_id: int) -> Path:
    # settings.documentos_dir é configurável (.env) — o caminho definitivo de rede/servidor
    # ainda será definido pelo cliente; por enquanto isso pode até ser uma pasta local.
    pasta = Path(settings.documentos_dir) / f"patrimonio_{patrimonio_id}"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def _montar_saida(d: Documento) -> dict:
    dados = DocumentoOut.model_validate(d).model_dump()
    dados["usuario_nome"] = d.usuario.nome if d.usuario else None
    return dados


@router.get("", response_model=list[DocumentoOut])
def listar(
    patrimonio_id: int,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(obter_usuario_atual),
):
    patrimonio = db.query(Patrimonio).filter(Patrimonio.id == patrimonio_id).first()
    if patrimonio is None:
        raise HTTPException(status_code=404, detail="Patrimônio não encontrado.")

    documentos = (
        db.query(Documento)
        .options(joinedload(Documento.usuario))
        .filter(Documento.patrimonio_id == patrimonio_id)
        .order_by(Documento.enviado_em.desc())
        .all()
    )
    return [_montar_saida(d) for d in documentos]


@router.post("", response_model=DocumentoOut, status_code=201)
def enviar(
    patrimonio_id: int,
    tipo: str = Form(...),
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario: UsuarioLogado = Depends(exigir_perfis(*PERFIS_QUE_ANEXAM)),
):
    if tipo not in TIPOS_DOCUMENTO:
        raise HTTPException(status_code=400, detail=f"Tipo inválido. Use um de: {TIPOS_DOCUMENTO}")

    patrimonio = db.query(Patrimonio).filter(Patrimonio.id == patrimonio_id).first()
    if patrimonio is None:
        raise HTTPException(status_code=404, detail="Patrimônio não encontrado.")

    nome_original = arquivo.filename or "documento"
    extensao = Path(nome_original).suffix
    nome_no_disco = f"{uuid.uuid4().hex}{extensao}"

    pasta = _pasta_do_patrimonio(patrimonio_id)
    destino = pasta / nome_no_disco
    with destino.open("wb") as saida:
        saida.write(arquivo.file.read())

    novo = Documento(
        patrimonio_id=patrimonio_id,
        tipo=tipo,
        nome_arquivo=nome_original,
        caminho=f"patrimonio_{patrimonio_id}/{nome_no_disco}",
        usuario_id=usuario.id,
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return _montar_saida(novo)


@router.get("/{documento_id}/download")
def baixar(
    patrimonio_id: int,
    documento_id: int,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(obter_usuario_atual),
):
    documento = (
        db.query(Documento)
        .filter(Documento.id == documento_id, Documento.patrimonio_id == patrimonio_id)
        .first()
    )
    if documento is None:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")

    caminho_completo = Path(settings.documentos_dir) / documento.caminho
    if not caminho_completo.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado no armazenamento.")

    return FileResponse(caminho_completo, filename=documento.nome_arquivo)
