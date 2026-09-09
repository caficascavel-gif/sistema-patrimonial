from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QHeaderView, QMessageBox, QStatusBar
)

from app.api_client import cliente_api, ErroAPI, ErroConexao
from app.ui.ficha_patrimonio.ficha_window import JanelaFichaPatrimonio
from app.ui.relatorios.janela_relatorios import JanelaRelatorios
from app.ui.dashboard import JanelaDashboard
from app.ui.auditoria import JanelaAuditoria

# Emojis de status, conforme o indicador pedido na especificação (seção 7 e 9)
SITUACAO_ICONE = {
    "Em uso": "🟢",
    "Disponível": "🟢",
    "Em manutenção": "🟠",
    "Em garantia": "🟠",
    "Emprestado": "🔵",
    "Baixado": "⚪",
    "Descartado": "⚪",
}

COLUNAS = ["Patrimônio", "Equipamento", "Local", "Situação", "Cadastro"]


class JanelaPrincipal(QMainWindow):
    def __init__(self, usuario_logado: dict):
        super().__init__()
        self.usuario_logado = usuario_logado
        self.resultados_atuais: list[dict] = []

        self.setWindowTitle("Sistema de Controle Patrimonial")
        self.resize(1000, 600)

        self._montar_interface()
        self._pesquisar()  # já carrega a lista completa ao abrir

    def _montar_interface(self):
        central = QWidget(self)
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Cabeçalho com usuário logado
        cabecalho = QHBoxLayout()
        cabecalho.addWidget(QLabel(f"<b>PATRIMÔNIOS</b>"))
        cabecalho.addStretch()
        botao_dashboard = QPushButton("📈 Dashboard", self)
        botao_dashboard.clicked.connect(self._abrir_dashboard)
        cabecalho.addWidget(botao_dashboard)
        botao_relatorios = QPushButton("📊 Relatórios", self)
        botao_relatorios.clicked.connect(self._abrir_relatorios)
        cabecalho.addWidget(botao_relatorios)
        if self.usuario_logado.get("perfil_nome") == "Administrador":
            botao_auditoria = QPushButton("🕵️ Auditoria", self)
            botao_auditoria.clicked.connect(self._abrir_auditoria)
            cabecalho.addWidget(botao_auditoria)
        cabecalho.addWidget(QLabel(f"{self.usuario_logado['nome']} ({self.usuario_logado['perfil_nome']})"))
        layout.addLayout(cabecalho)

        # Campo de pesquisa
        linha_busca = QHBoxLayout()
        self.campo_busca = QLineEdit(self)
        self.campo_busca.setPlaceholderText("🔎 patrimônio, equipamento, IPM, empenho, fornecedor, número de série…")
        self.campo_busca.returnPressed.connect(self._pesquisar)
        botao_buscar = QPushButton("Pesquisar", self)
        botao_buscar.clicked.connect(self._pesquisar)
        linha_busca.addWidget(self.campo_busca)
        linha_busca.addWidget(botao_buscar)
        layout.addLayout(linha_busca)

        # Tabela de resultados
        self.tabela = QTableWidget(self)
        self.tabela.setColumnCount(len(COLUNAS))
        self.tabela.setHorizontalHeaderLabels(COLUNAS)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setSelectionMode(QTableWidget.SingleSelection)
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela.doubleClicked.connect(self._abrir_ficha_selecionada)
        layout.addWidget(self.tabela)

        self.setStatusBar(QStatusBar(self))

    def _pesquisar(self):
        termo = self.campo_busca.text().strip()
        try:
            self.resultados_atuais = cliente_api.buscar_patrimonios(termo)
        except ErroConexao as erro:
            QMessageBox.critical(self, "Erro de conexão", str(erro))
            return
        except ErroAPI as erro:
            QMessageBox.warning(self, "Erro na pesquisa", erro.mensagem)
            return

        self._preencher_tabela(self.resultados_atuais)
        self.statusBar().showMessage(f"{len(self.resultados_atuais)} patrimônio(s) encontrado(s).")

    def _preencher_tabela(self, patrimonios: list[dict]):
        self.tabela.setRowCount(len(patrimonios))
        for linha, p in enumerate(patrimonios):
            situacao = p.get("situacao_atual", "")
            icone = SITUACAO_ICONE.get(situacao, "")
            indicador_cadastro = "🟢" if p.get("status_cadastro") == "completo" else "🟡"

            valores = [
                p.get("numero_patrimonio", ""),
                p.get("item_descricao") or "—",
                p.get("local_descricao") or "—",
                f"{icone} {situacao}".strip(),
                indicador_cadastro,
            ]
            for coluna, texto in enumerate(valores):
                item = QTableWidgetItem(texto)
                if coluna == 0:
                    item.setData(Qt.UserRole, p.get("id"))  # guarda o id do patrimônio na própria célula
                self.tabela.setItem(linha, coluna, item)

    def _abrir_dashboard(self):
        JanelaDashboard(parent=self).exec()

    def _abrir_auditoria(self):
        JanelaAuditoria(parent=self).exec()

    def _abrir_relatorios(self):
        JanelaRelatorios(parent=self).exec()

    def _abrir_ficha_selecionada(self):
        linha = self.tabela.currentRow()
        if linha < 0:
            return
        lista_ids = [p["id"] for p in self.resultados_atuais]
        ficha = JanelaFichaPatrimonio(lista_ids_resultado=lista_ids, indice_atual=linha, parent=self)
        ficha.exec()
        self._pesquisar()  # recarrega a lista, caso algo tenha sido alterado na ficha
