import sys
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

if getattr(sys, "frozen", False):
    # Rodando como .exe gerado pelo PyInstaller: o .env deve ficar do lado do .exe.
    # sys.executable aponta pro .exe em si (não para a pasta temporária onde o
    # PyInstaller descompacta o programa) — é o comportamento certo aqui.
    _BASE_DIR = Path(sys.executable).resolve().parent
else:
    # Rodando via "python" normal (desenvolvimento): .env fica na pasta backend/.
    _BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Configurações lidas do arquivo .env (nunca versionar o .env real)."""

    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480  # 8 horas, conforme definido

    # Pasta onde os documentos anexados são salvos. Fica configurável por enquanto —
    # o caminho definitivo (rede/servidor) ainda não foi definido pelo cliente.
    documentos_dir: str = "./armazenamento/documentos"

    model_config = SettingsConfigDict(env_file=str(_BASE_DIR / ".env"), env_file_encoding="utf-8")


settings = Settings()
