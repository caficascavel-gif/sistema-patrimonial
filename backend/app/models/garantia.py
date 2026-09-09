from sqlalchemy import Column, Date, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base

SITUACOES_GARANTIA = (
    "Aguardando envio", "Enviado", "Aguardando fornecedor",
    "Em análise", "Concluído", "Retornado", "Sem solução",
)


class Garantia(Base):
    __tablename__ = "garantias"

    id = Column(Integer, primary_key=True, index=True)
    patrimonio_id = Column(Integer, ForeignKey("patrimonios.id"), nullable=False)
    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"), nullable=True)
    data_envio = Column(Date)
    protocolo = Column(String(80))
    motivo = Column(String(255))
    problema = Column(Text)
    previsao_retorno = Column(Date)
    situacao = Column(Enum(*SITUACOES_GARANTIA, name="situacao_garantia"),
                       nullable=False, default="Aguardando envio")
    observacoes = Column(Text)
    movimentacao_retorno_id = Column(Integer, ForeignKey("movimentacoes.id"), nullable=True)

    fornecedor = relationship("Fornecedor")
    movimentacao_retorno = relationship("Movimentacao")
    patrimonio = relationship("Patrimonio")
