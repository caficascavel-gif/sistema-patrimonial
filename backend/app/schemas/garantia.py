from datetime import date

from pydantic import BaseModel, ConfigDict

SITUACOES_GARANTIA = (
    "Aguardando envio", "Enviado", "Aguardando fornecedor",
    "Em análise", "Concluído", "Retornado", "Sem solução",
)


class GarantiaCreate(BaseModel):
    fornecedor_id: int | None = None
    data_envio: date | None = None
    protocolo: str | None = None
    motivo: str | None = None
    problema: str | None = None
    previsao_retorno: date | None = None
    situacao: str = "Aguardando envio"
    observacoes: str | None = None


class GarantiaUpdate(BaseModel):
    fornecedor_id: int | None = None
    data_envio: date | None = None
    protocolo: str | None = None
    motivo: str | None = None
    problema: str | None = None
    previsao_retorno: date | None = None
    situacao: str | None = None
    observacoes: str | None = None


class GarantiaRetorno(BaseModel):
    """Usado no botão 'REGISTRAR RETORNO DA GARANTIA' — o destino é escolhido pelo usuário."""
    destino: str
    observacao: str | None = None


class GarantiaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patrimonio_id: int
    fornecedor_id: int | None
    data_envio: date | None
    protocolo: str | None
    motivo: str | None
    problema: str | None
    previsao_retorno: date | None
    situacao: str
    observacoes: str | None
    movimentacao_retorno_id: int | None

    fornecedor_nome: str | None = None
