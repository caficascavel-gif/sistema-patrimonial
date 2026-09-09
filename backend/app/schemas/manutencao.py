from datetime import date

from pydantic import BaseModel, ConfigDict

SITUACOES_MANUTENCAO = (
    "Em análise", "Em manutenção", "Aguardando peça", "Aguardando fornecedor",
    "Resolvido", "Sem conserto", "Encaminhado para garantia",
)


class ManutencaoCreate(BaseModel):
    data: date
    problema_relatado: str | None = None
    servico_realizado: str | None = None
    pecas_utilizadas: str | None = None
    custo: float | None = None
    fornecedor_id: int | None = None
    situacao: str = "Em análise"
    conclusao: str | None = None
    observacoes: str | None = None


class ManutencaoUpdate(BaseModel):
    servico_realizado: str | None = None
    pecas_utilizadas: str | None = None
    custo: float | None = None
    fornecedor_id: int | None = None
    situacao: str | None = None
    conclusao: str | None = None
    observacoes: str | None = None


class ManutencaoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patrimonio_id: int
    data: date
    problema_relatado: str | None
    responsavel_id: int | None
    servico_realizado: str | None
    pecas_utilizadas: str | None
    custo: float | None
    fornecedor_id: int | None
    situacao: str
    conclusao: str | None
    observacoes: str | None

    responsavel_nome: str | None = None
    fornecedor_nome: str | None = None
