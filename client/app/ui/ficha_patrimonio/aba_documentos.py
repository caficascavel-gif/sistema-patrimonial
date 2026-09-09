from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QFileDialog
)

from app.api_client import cliente_api, ErroAPI, ErroConexao

TIPOS_DOCUMENTO = (
    "Nota Fiscal", "Empenho", "Termo de garantia", "Ordem de serviço",
    "Laudo técnico", "Comunicação do fornecedor", "Outros",
)

COLUNAS = ["Tipo", "Arquivo", "Enviado em", "Enviado por"]


class AbaDocumentos(QWidget):
    def __init__(self, parent_ficha):
        super().__init__()
        self.parent_ficha = parent_ficha
        self.patrimonio_id: int | None = None
        self.documentos: list[dict] = []
        self._montar_interface()

    def _montar_interface(self):
        layout = QVBoxLayout(self)

        linha_topo = QHBoxLayout()
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(TIPOS_DOCUMENTO)
        botao_anexar = QPushButton("📎 Anexar arquivo")
        botao_anexar.clicked.connect(self._anexar)
        linha_topo.addWidget(self.combo_tipo)
        linha_topo.addWidget(botao_anexar)
        linha_topo.addStretch()
        layout.addLayout(linha_topo)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(len(COLUNAS))
        self.tabela.setHorizontalHeaderLabels(COLUNAS)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela.doubleClicked.connect(self._baixar_selecionado)
        layout.addWidget(self.tabela)

    def carregar(self, patrimonio_id: int):
        self.patrimonio_id = patrimonio_id
        try:
            self.documentos = cliente_api.listar_documentos(patrimonio_id)
        except (ErroAPI, ErroConexao) as erro:
            QMessageBox.warning(self, "Erro ao carregar documentos", str(erro))
            self.documentos = []

        self.tabela.setRowCount(len(self.documentos))
        for linha, doc in enumerate(self.documentos):
            valores = [
                doc["tipo"], doc["nome_arquivo"],
                doc["enviado_em"].replace("T", " ")[:16],
                doc.get("usuario_nome") or "—",
            ]
            for coluna, texto in enumerate(valores):
                item = QTableWidgetItem(texto)
                if coluna == 0:
                    item.setData(Qt.UserRole, doc["id"])
                self.tabela.setItem(linha, coluna, item)

    def _anexar(self):
        if self.patrimonio_id is None:
            return
        caminho, _ = QFileDialog.getOpenFileName(self, "Selecionar arquivo")
        if not caminho:
            return
        try:
            cliente_api.enviar_documento(self.patrimonio_id, self.combo_tipo.currentText(), caminho)
        except ErroConexao as erro:
            QMessageBox.critical(self, "Erro de conexão", str(erro))
            return
        except ErroAPI as erro:
            QMessageBox.warning(self, "Não foi possível enviar", erro.mensagem)
            return
        self.carregar(self.patrimonio_id)

    def _baixar_selecionado(self):
        linha = self.tabela.currentRow()
        if linha < 0 or linha >= len(self.documentos):
            return
        doc = self.documentos[linha]
        destino, _ = QFileDialog.getSaveFileName(self, "Salvar como", doc["nome_arquivo"])
        if not destino:
            return
        try:
            cliente_api.baixar_documento(self.patrimonio_id, doc["id"], destino)
        except (ErroAPI, ErroConexao) as erro:
            QMessageBox.warning(self, "Não foi possível baixar", str(erro))
            return
        QMessageBox.information(self, "Concluído", f"Arquivo salvo em:\n{destino}")
