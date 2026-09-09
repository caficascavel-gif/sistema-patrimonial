from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), unique=True, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)


class Marca(Base):
    __tablename__ = "marcas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), unique=True, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)

    modelos = relationship("Modelo", back_populates="marca")


class Modelo(Base):
    __tablename__ = "modelos"

    id = Column(Integer, primary_key=True, index=True)
    marca_id = Column(Integer, ForeignKey("marcas.id"), nullable=False)
    nome = Column(String(120), nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)

    marca = relationship("Marca", back_populates="modelos")


class Fornecedor(Base):
    __tablename__ = "fornecedores"

    id = Column(Integer, primary_key=True, index=True)
    razao_social = Column(String(200), nullable=False)
    nome_fantasia = Column(String(200))
    cnpj = Column(String(20), unique=True)
    telefone = Column(String(30))
    email = Column(String(150))
    endereco = Column(String(255))
    contato = Column(String(150))
    observacoes = Column(Text)
    ativo = Column(Boolean, default=True, nullable=False)
