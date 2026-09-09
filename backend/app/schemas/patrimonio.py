from datetime import datetime

from pydantic import BaseModel, ConfigDict

SITUACOES = (
    "Em uso", "Disponível", "Em manutenção", "Em garantia",
    "Emprestado", "Baixado", "Descartado",
)


class PatrimonioCreate(BaseModel):
    """
    Só 'numero_patrimonio' e 'item_id' são obrigatórios — o resto pode ser
    preenchido depois por outra pessoa/setor (cadastro parcial, conforme spec).
    """
    numero_patrimonio: str
    item_id: int

    ipm: str | None = None
    numero_serie: str | None = None
    aquisicao_id: int | None = None
    empenho_id: int | None = None

    secretaria_id: int | None = None
    setor_id: int | None = None
    local_id: int | None = None
    responsavel_id: int | None = None

    situacao_atual: str = "Disponível"


class PatrimonioUpdate(BaseModel):
    """Todos os campos opcionais — usado para completar um cadastro parcial."""
    ipm: str | None = None
    numero_serie: str | None = None
    aquisicao_id: int | None = None
    empenho_id: int | None = None

    secretaria_id: int | None = None
    setor_id: int | None = None
    local_id: int | None = None
    responsavel_id: int | None = None

    situacao_atual: str | None = None


class PatrimonioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero_patrimonio: str
    item_id: int
    ipm: str | None
    numero_serie: str | None
    aquisicao_id: int | None
    empenho_id: int | None
    secretaria_id: int | None
    setor_id: int | None
    local_id: int | None
    responsavel_id: int | None
    situacao_atual: str
    criado_em: datetime
    atualizado_em: datetime

    # calculados na hora da resposta (não existem como coluna no banco)
    status_cadastro: str = "incompleto"   # "completo" | "incompleto"
    pendencias: list[str] = []
    item_descricao: str | None = None      # nome do equipamento, para exibir na lista
    local_descricao: str | None = None     # "Setor / Local", para exibir na lista
