from datetime import date as date_type

from sqlalchemy import Column, Date, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.database import Base

SITUACOES_MANUTENCAO = (
    "Em análise", "Em manutenção", "Aguardando peça", "Aguardando fornecedor",
    "Resolvido", "Sem conserto", "Encaminhado para garantia",
)


class Manutencao(Base):
    __tablename__ = "manutencoes"

    id = Column(Integer, primary_key=True, index=True)
    patrimonio_id = Column(Integer, ForeignKey("patrimonios.id"), nullable=False)
    data = Column(Date, nullable=False)
    problema_relatado = Column(Text)
    responsavel_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    servico_realizado = Column(Text)
    pecas_utilizadas = Column(Text)
    custo = Column(Numeric(14, 2))
    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"), nullable=True)
    situacao = Column(Enum(*SITUACOES_MANUTENCAO, name="situacao_manutencao"),
                       nullable=False, default="Em análise")
    conclusao = Column(Text)
    observacoes = Column(Text)

    responsavel = relationship("Usuario")
    fornecedor = relationship("Fornecedor")
    patrimonio = relationship("Patrimonio")
