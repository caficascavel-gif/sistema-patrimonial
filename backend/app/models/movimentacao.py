from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base

TIPOS_MOVIMENTACAO = (
    "Entrada", "Transferência", "Empréstimo", "Engenharia Clínica",
    "Manutenção", "Garantia", "Retorno de garantia", "Retorno de manutenção",
    "Baixa", "Descarte", "Outros",
)


class Movimentacao(Base):
    """
    Histórico do patrimônio. Regra de ouro (seção 14/32 da especificação):
    NUNCA apagar ou sobrescrever um registro já criado — é sempre 'append only'.
    """

    __tablename__ = "movimentacoes"

    id = Column(Integer, primary_key=True, index=True)
    patrimonio_id = Column(Integer, ForeignKey("patrimonios.id"), nullable=False)
    data = Column(DateTime, default=datetime.utcnow, nullable=False)
    tipo = Column(Enum(*TIPOS_MOVIMENTACAO, name="tipo_movimentacao"), nullable=False)
    origem = Column(String(200))
    destino = Column(String(200))
    responsavel_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    motivo = Column(String(255))
    observacao = Column(Text)

    responsavel = relationship("Usuario")
