from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base

SITUACOES_PATRIMONIO = (
    "Em uso", "Disponível", "Em manutenção", "Em garantia",
    "Emprestado", "Baixado", "Descartado",
)


class Patrimonio(Base):
    """
    Representa o bem físico individual. A localização/situação aqui é a ATUAL
    (desnormalizada por performance) — a verdade histórica completa vive em
    'movimentacoes' (Etapa 7). Nunca sobrescrever o histórico ao mudar isso.
    """

    __tablename__ = "patrimonios"

    id = Column(Integer, primary_key=True, index=True)
    numero_patrimonio = Column(String(40), unique=True, nullable=False, index=True)
    ipm = Column(String(40))
    item_id = Column(Integer, ForeignKey("itens.id"), nullable=False)
    numero_serie = Column(String(100))
    aquisicao_id = Column(Integer, ForeignKey("aquisicoes.id"), nullable=True)
    empenho_id = Column(Integer, ForeignKey("empenhos.id"), nullable=True)

    secretaria_id = Column(Integer, ForeignKey("secretarias.id"), nullable=True)
    setor_id = Column(Integer, ForeignKey("setores.id"), nullable=True)
    local_id = Column(Integer, ForeignKey("locais.id"), nullable=True)
    responsavel_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    situacao_atual = Column(Enum(*SITUACOES_PATRIMONIO, name="situacao_patrimonio"),
                             nullable=False, default="Disponível")

    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    item = relationship("Item")
    aquisicao = relationship("Aquisicao")
    empenho = relationship("Empenho")
    secretaria = relationship("Secretaria")
    setor = relationship("Setor")
    local = relationship("Local")
    responsavel = relationship("Usuario")
