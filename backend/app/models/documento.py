from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base

TIPOS_DOCUMENTO = (
    "Nota Fiscal", "Empenho", "Termo de garantia", "Ordem de serviço",
    "Laudo técnico", "Comunicação do fornecedor", "Outros",
)


class Documento(Base):
    __tablename__ = "documentos"

    id = Column(Integer, primary_key=True, index=True)
    patrimonio_id = Column(Integer, ForeignKey("patrimonios.id"), nullable=False)
    tipo = Column(Enum(*TIPOS_DOCUMENTO, name="tipo_documento"), nullable=False)
    nome_arquivo = Column(String(255), nullable=False)   # nome original, para exibição/download
    caminho = Column(String(500), nullable=False)         # caminho relativo dentro de settings.documentos_dir
    enviado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    usuario = relationship("Usuario")
