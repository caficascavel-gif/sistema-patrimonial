from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox
)

from app.api_client import cliente_api, ErroAPI, ErroConexao
from app.ui.ficha_patrimonio.dialogo_nova_garantia import DialogoNovaGarantia
from app.ui.ficha_patrimonio.dialogo_retorno_garantia import DialogoRetornoGarantia

COLUNAS = ["Fornecedor", "Protocolo", "Situação", "Previsão de retorno"]


class AbaGarantia(QWidget):
    def __init__(self, parent_ficha):
        super().__init__()
        self.parent_ficha = parent_ficha
        self.patrimonio_id: int | None = None
        self.registros: list[dict] = []
        self._montar_interface()

    def _montar_interface(self):
        layout = QVBoxLayout(self)

        linha_botoes = QHBoxLayout()
        self.botao_novo = QPushButton("Registrar envio para garantia")
        self.botao_novo.clicked.connect(self._abrir_novo)
        self.botao_retorno = QPushButton("REGISTRAR RETORNO DA GARANTIA")
        self.botao_retorno.clicked.connect(self._abrir_retorno)
        self.botao_retorno.setEnabled(False)
        linha_botoes.addWidget(self.botao_novo)
        linha_botoes.addWidget(self.botao_retorno)
        linha_botoes.addStretch()
        layout.addLayout(linha_botoes)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(len(COLUNAS))
        self.tabela.setHorizontalHeaderLabels(COLUNAS)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setSelectionMode(QTableWidget.SingleSelection)
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabela.itemSelectionChanged.connect(self._atualizar_estado_botao_retorno)
        layout.addWidget(self.tabela)

    def carregar(self, patrimonio_id: int):
        self.patrimonio_id = patrimonio_id
        try:
            self.registros = cliente_api.listar_garantias(patrimonio_id)
        except (ErroAPI, ErroConexao) as erro:
            QMessageBox.warning(self, "Erro ao carregar garantias", str(erro))
            self.registros = []

        self.tabela.setRowCount(len(self.registros))
        for linha, g in enumerate(self.registros):
            valores = [
                g.get("fornecedor_nome") or "—",
                g.get("protocolo") or "—",
                g["situacao"],
                g.get("previsao_retorno") or "—",
            ]
            for coluna, texto in enumerate(valores):
                item = QTableWidgetItem(texto)
                if coluna == 0:
                    item.setData(Qt.UserRole, g["id"])
                self.tabela.setItem(linha, coluna, item)

        self._atualizar_estado_botao_retorno()

    def _atualizar_estado_botao_retorno(self):
        linha = self.tabela.currentRow()
        habilita = False
        if 0 <= linha < len(self.registros):
            habilita = self.registros[linha]["situacao"] != "Retornado"
        self.botao_retorno.setEnabled(habilita)

    def _abrir_novo(self):
        if self.patrimonio_id is None:
            return
        dialogo = DialogoNovaGarantia(self.patrimonio_id, parent=self)
        if dialogo.exec():
            self.carregar(self.patrimonio_id)

    def _abrir_retorno(self):
        linha = self.tabela.currentRow()
        if linha < 0 or linha >= len(self.registros):
            QMessageBox.information(self, "Selecione uma garantia", "Selecione a garantia na tabela primeiro.")
            return
        garantia = self.registros[linha]
        dialogo = DialogoRetornoGarantia(self.patrimonio_id, garantia, parent=self)
        if dialogo.exec():
            self.carregar(self.patrimonio_id)
            # o retorno cria uma movimentação automática -> atualiza a aba Histórico também
            self.parent_ficha.recarregar_historico()
