from PySide6.QtWidgets import QMessageBox

from app.api_client import cliente_api, ErroAPI, ErroConexao
from app.ui.relatorios.tela_relatorio import TelaRelatorio

COLUNAS_AUDITORIA = [
    ("data_hora", "Data/hora"), ("usuario_nome", "Usuário"),
    ("numero_patrimonio", "Patrimônio"), ("campo", "Campo"),
    ("valor_anterior", "Antes"), ("valor_novo", "Depois"),
]


class JanelaAuditoria(TelaRelatorio):
    """Reaproveita a tela genérica de relatório para mostrar o log de auditoria (seção 25)."""

    def __init__(self, parent=None):
        try:
            registros = cliente_api.listar_auditoria()
        except ErroConexao as erro:
            QMessageBox.critical(parent, "Erro de conexão", str(erro))
            registros = []
        except ErroAPI as erro:
            QMessageBox.warning(parent, "Erro ao abrir auditoria", erro.mensagem)
            registros = []

        for registro in registros:
            registro["data_hora"] = registro["data_hora"].replace("T", " ")[:16]

        super().__init__("Auditoria", COLUNAS_AUDITORIA, registros, parent=parent)
