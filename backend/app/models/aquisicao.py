from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Aquisicao(Base):
    __tablename__ = "aquisicoes"

    id = Column(Integer, primary_key=True, index=True)
    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"), nullable=True)
    empenho_id = Column(Integer, ForeignKey("empenhos.id"), nullable=True)
    nota_fiscal = Column(String(60))
    data_compra = Column(Date)
    data_entrada = Column(Date)
    valor = Column(Numeric(14, 2))
    observacoes = Column(Text)

    fornecedor = relationship("Fornecedor")
    empenho = relationship("Empenho")
