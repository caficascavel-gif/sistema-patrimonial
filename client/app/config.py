"""
Guarda a configuração local do cliente (hoje só o endereço da API) em um
arquivo JSON na pasta de dados do usuário do Windows (%APPDATA%).
Em outros sistemas, cai num equivalente razoável — útil para testar aqui no Linux.
"""
import json
import os
from pathlib import Path


def _pasta_config() -> Path:
    base = os.environ.get("APPDATA") or os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    pasta = Path(base) / "SistemaPatrimonial"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


ARQUIVO_CONFIG = _pasta_config() / "config.json"


def carregar_config() -> dict:
    if ARQUIVO_CONFIG.exists():
        try:
            return json.loads(ARQUIVO_CONFIG.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def salvar_config(dados: dict) -> None:
    atual = carregar_config()
    atual.update(dados)
    ARQUIVO_CONFIG.write_text(json.dumps(atual, indent=2, ensure_ascii=False), encoding="utf-8")


def obter_url_api() -> str | None:
    return carregar_config().get("api_url")


def definir_url_api(url: str) -> None:
    salvar_config({"api_url": url.rstrip("/")})
