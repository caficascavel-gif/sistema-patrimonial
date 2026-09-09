from pydantic import BaseModel, ConfigDict


class ItemBase(BaseModel):
    descricao: str
    categoria_id: int | None = None
    marca_id: int | None = None
    modelo_id: int | None = None
    fabricante: str | None = None
    caracteristicas: str | None = None
    observacoes: str | None = None
    ativo: bool = True


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    descricao: str | None = None
    categoria_id: int | None = None
    marca_id: int | None = None
    modelo_id: int | None = None
    fabricante: str | None = None
    caracteristicas: str | None = None
    observacoes: str | None = None
    ativo: bool | None = None


class ItemOut(ItemBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
