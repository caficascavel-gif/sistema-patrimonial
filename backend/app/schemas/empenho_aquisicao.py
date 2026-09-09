from datetime import date

from pydantic import BaseModel, ConfigDict


# ---- Empenho ----
class EmpenhoBase(BaseModel):
    numero: str
    ano: int
    fornecedor_id: int | None = None
    processo: str | None = None
    data: date | None = None
    valor: float | None = None
    observacoes: str | None = None


class EmpenhoCreate(EmpenhoBase):
    pass


class EmpenhoUpdate(BaseModel):
    numero: str | None = None
    ano: int | None = None
    fornecedor_id: int | None = None
    processo: str | None = None
    data: date | None = None
    valor: float | None = None
    observacoes: str | None = None


class EmpenhoOut(EmpenhoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---- Aquisição ----
class AquisicaoBase(BaseModel):
    fornecedor_id: int | None = None
    empenho_id: int | None = None
    nota_fiscal: str | None = None
    data_compra: date | None = None
    data_entrada: date | None = None
    valor: float | None = None
    observacoes: str | None = None


class AquisicaoCreate(AquisicaoBase):
    pass


class AquisicaoUpdate(AquisicaoBase):
    pass


class AquisicaoOut(AquisicaoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
