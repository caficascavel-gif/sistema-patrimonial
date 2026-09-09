from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    usuario = Column(String(60), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)
    perfil_id = Column(Integer, ForeignKey("perfis.id"), nullable=False)
    secretaria_id = Column(Integer, ForeignKey("secretarias.id"), nullable=True)
    setor_id = Column(Integer, ForeignKey("setores.id"), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)

    perfil = relationship("Perfil")
    secretaria = relationship("Secretaria")
    setor = relationship("Setor")
