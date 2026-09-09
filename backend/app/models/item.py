from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Item(Base):
    """Representa o TIPO de equipamento (ex: 'Fotopolimerizador'), não o bem físico individual."""

    __tablename__ = "itens"

    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String(200), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)
    marca_id = Column(Integer, ForeignKey("marcas.id"), nullable=True)
    modelo_id = Column(Integer, ForeignKey("modelos.id"), nullable=True)
    fabricante = Column(String(150))
    caracteristicas = Column(Text)
    observacoes = Column(Text)
    ativo = Column(Boolean, default=True, nullable=False)

    categoria = relationship("Categoria")
    marca = relationship("Marca")
    modelo = relationship("Modelo")
