from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Secretaria(Base):
    __tablename__ = "secretarias"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), unique=True, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)

    setores = relationship("Setor", back_populates="secretaria")


class Setor(Base):
    __tablename__ = "setores"

    id = Column(Integer, primary_key=True, index=True)
    secretaria_id = Column(Integer, ForeignKey("secretarias.id"), nullable=False)
    nome = Column(String(150), nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)

    secretaria = relationship("Secretaria", back_populates="setores")
    locais = relationship("Local", back_populates="setor")


class Local(Base):
    __tablename__ = "locais"

    id = Column(Integer, primary_key=True, index=True)
    setor_id = Column(Integer, ForeignKey("setores.id"), nullable=False)
    nome = Column(String(150), nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)

    setor = relationship("Setor", back_populates="locais")
