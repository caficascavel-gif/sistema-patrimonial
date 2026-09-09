from datetime import datetime

from pydantic import BaseModel, ConfigDict

TIPOS_MOVIMENTACAO = (
    "Entrada", "Transferência", "Empréstimo", "Engenharia Clínica",
    "Manutenção", "Garantia", "Retorno de garantia", "Retorno de manutenção",
    "Baixa", "Descarte", "Outros",
)


class MovimentacaoCreate(BaseModel):
    tipo: str
    origem: str | None = None
    destino: str | None = None
    motivo: str | None = None
    observacao: str | None = None


class MovimentacaoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patrimonio_id: int
    data: datetime
    tipo: str
    origem: str | None
    destino: str | None
    responsavel_id: int
    motivo: str | None
    observacao: str | None
    responsavel_nome: str | None = None  # preenchido na resposta, não é coluna
