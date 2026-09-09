from datetime import datetime

from pydantic import BaseModel, ConfigDict

TIPOS_DOCUMENTO = (
    "Nota Fiscal", "Empenho", "Termo de garantia", "Ordem de serviço",
    "Laudo técnico", "Comunicação do fornecedor", "Outros",
)


class DocumentoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patrimonio_id: int
    tipo: str
    nome_arquivo: str
    enviado_em: datetime
    usuario_id: int | None
    usuario_nome: str | None = None
