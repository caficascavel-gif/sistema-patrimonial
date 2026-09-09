from sqlalchemy import Boolean, Column, Integer, String

from app.database import Base


class Perfil(Base):
    __tablename__ = "perfis"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(60), unique=True, nullable=False)
    descricao = Column(String(255))
    ativo = Column(Boolean, default=True, nullable=False)
