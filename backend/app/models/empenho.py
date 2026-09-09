from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class Empenho(Base):
    __tablename__ = "empenhos"
    __table_args__ = (UniqueConstraint("numero", "ano", name="uq_empenho"),)

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(40), nullable=False)
    ano = Column(Integer, nullable=False)
    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"), nullable=True)
    processo = Column(String(60))
    data = Column(Date)
    valor = Column(Numeric(14, 2))
    observacoes = Column(Text)

    fornecedor = relationship("Fornecedor")
