from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Anotacao(Base):
    """Histórico de anotações do patrimônio. Nunca editar ou apagar (seção 18)."""

    __tablename__ = "anotacoes"

    id = Column(Integer, primary_key=True, index=True)
    patrimonio_id = Column(Integer, ForeignKey("patrimonios.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    data_hora = Column(DateTime, default=datetime.utcnow, nullable=False)
    texto = Column(Text, nullable=False)

    usuario = relationship("Usuario")
