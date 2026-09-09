from pydantic import BaseModel, ConfigDict


# ---- Categoria ----
class CategoriaBase(BaseModel):
    nome: str
    ativo: bool = True


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaOut(CategoriaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---- Marca ----
class MarcaBase(BaseModel):
    nome: str
    ativo: bool = True


class MarcaCreate(MarcaBase):
    pass


class MarcaOut(MarcaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---- Modelo ----
class ModeloBase(BaseModel):
    marca_id: int
    nome: str
    ativo: bool = True


class ModeloCreate(ModeloBase):
    pass


class ModeloOut(ModeloBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---- Fornecedor ----
class FornecedorBase(BaseModel):
    razao_social: str
    nome_fantasia: str | None = None
    cnpj: str | None = None
    telefone: str | None = None
    email: str | None = None
    endereco: str | None = None
    contato: str | None = None
    observacoes: str | None = None
    ativo: bool = True


class FornecedorCreate(FornecedorBase):
    pass


class FornecedorUpdate(BaseModel):
    razao_social: str | None = None
    nome_fantasia: str | None = None
    cnpj: str | None = None
    telefone: str | None = None
    email: str | None = None
    endereco: str | None = None
    contato: str | None = None
    observacoes: str | None = None
    ativo: bool | None = None


class FornecedorOut(FornecedorBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---- Secretaria / Setor / Local ----
class SecretariaBase(BaseModel):
    nome: str
    ativo: bool = True


class SecretariaCreate(SecretariaBase):
    pass


class SecretariaOut(SecretariaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class SetorBase(BaseModel):
    secretaria_id: int
    nome: str
    ativo: bool = True


class SetorCreate(SetorBase):
    pass


class SetorOut(SetorBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class LocalBase(BaseModel):
    setor_id: int
    nome: str
    ativo: bool = True


class LocalCreate(LocalBase):
    pass


class LocalOut(LocalBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
