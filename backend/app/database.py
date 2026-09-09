from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# pool_pre_ping evita erros de "conexão caiu" quando o app fica ocioso por muito tempo,
# comum em sistemas usados o dia inteiro em rede interna.
engine = create_engine(settings.database_url, pool_pre_ping=True, pool_recycle=3600)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency do FastAPI: abre uma sessão por requisição e sempre fecha ao final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
