from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditoriaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    data_hora: datetime
    patrimonio_id: int | None
    entidade: str
    entidade_id: int
    acao: str
    campo: str | None
    valor_anterior: str | None
    valor_novo: str | None

    usuario_nome: str | None = None
    numero_patrimonio: str | None = None
