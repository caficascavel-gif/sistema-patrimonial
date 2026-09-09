from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel, QMessageBox

from app.api_client import cliente_api, ErroAPI, ErroConexao
from app.ui.relatorios.tela_relatorio import TelaRelatorio

COLUNAS_PATRIMONIO_GERAL = [
    ("numero_patrimonio", "Patrimônio"), ("equipamento", "Equipamento"),
    ("setor", "Setor"), ("local", "Local"), ("situacao", "Situação"),
    ("fornecedor", "Fornecedor"), ("ne", "NE"),
]
COLUNAS_INCOMPLETOS = COLUNAS_PATRIMONIO_GERAL + [("pendencias", "Pendências")]
COLUNAS_MANUTENCAO = [
    ("numero_patrimonio", "Patrimônio"), ("equipamento", "Equipamento"),
    ("data", "Data"), ("situacao", "Situação"),
    ("problema_relatado", "Problema relatado"), ("responsavel", "Responsável"),
]
COLUNAS_GARANTIA = [
    ("numero_patrimonio", "Patrimônio"), ("equipamento", "Equipamento"),
    ("fornecedor", "Fornecedor"), ("situacao", "Situação"),
    ("data_envio", "Envio"), ("previsao_retorno", "Previsão de retorno"),
]

RELATORIOS_DISPONIVEIS = [
    ("Patrimônio geral", "relatorio_patrimonio_geral", COLUNAS_PATRIMONIO_GERAL),
    ("Equipamentos em manutenção", "relatorio_em_manutencao", COLUNAS_MANUTENCAO),
    ("Equipamentos em garantia", "relatorio_em_garantia", COLUNAS_GARANTIA),
    ("Equipamentos por setor", "relatorio_por_setor", COLUNAS_PATRIMONIO_GERAL),
    ("Equipamentos por fornecedor", "relatorio_por_fornecedor", COLUNAS_PATRIMONIO_GERAL),
    ("Equipamentos por empenho", "relatorio_por_empenho", COLUNAS_PATRIMONIO_GERAL),
    ("Patrimônios sem informações completas", "relatorio_incompletos", COLUNAS_INCOMPLETOS),
]


class JanelaRelatorios(QDialog):
    """Lista os relatórios da seção 27 da especificação; cada um abre na TelaRelatorio genérica."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Relatórios")
        self.setMinimumWidth(360)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b>Selecione um relatório:</b>"))
        for titulo, nome_metodo, colunas in RELATORIOS_DISPONIVEIS:
            botao = QPushButton(titulo)
            botao.clicked.connect(lambda _=False, t=titulo, m=nome_metodo, c=colunas: self._abrir(t, m, c))
            layout.addWidget(botao)

    def _abrir(self, titulo: str, nome_metodo: str, colunas: list):
        try:
            metodo = getattr(cliente_api, nome_metodo)
            linhas = metodo()
        except ErroConexao as erro:
            QMessageBox.critical(self, "Erro de conexão", str(erro))
            return
        except ErroAPI as erro:
            QMessageBox.warning(self, "Erro ao gerar relatório", erro.mensagem)
            return

        tela = TelaRelatorio(titulo, colunas, linhas, parent=self)
        tela.exec()
