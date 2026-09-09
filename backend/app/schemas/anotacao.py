from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AnotacaoCreate(BaseModel):
    texto: str


class AnotacaoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patrimonio_id: int
    usuario_id: int
    data_hora: datetime
    texto: str
    usuario_nome: str | None = None
