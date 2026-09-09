from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Auditoria(Base):
    """Registro de alterações importantes (seção 25). Só é criado pelo sistema — nunca editado/apagado."""

    __tablename__ = "auditoria"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    data_hora = Column(DateTime, default=datetime.utcnow, nullable=False)
    patrimonio_id = Column(Integer, ForeignKey("patrimonios.id"), nullable=True)
    entidade = Column(String(60), nullable=False)     # ex: 'patrimonio'
    entidade_id = Column(Integer, nullable=False)
    acao = Column(String(60), nullable=False)          # ex: 'atualizar_localizacao'
    campo = Column(String(80))
    valor_anterior = Column(Text)
    valor_novo = Column(Text)

    usuario = relationship("Usuario")
    patrimonio = relationship("Patrimonio")
