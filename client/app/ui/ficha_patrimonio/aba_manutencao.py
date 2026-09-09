from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox
)

from app.api_client import cliente_api, ErroAPI, ErroConexao
from app.ui.ficha_patrimonio.dialogo_nova_manutencao import DialogoNovaManutencao
from app.ui.ficha_patrimonio.dialogo_editar_manutencao import DialogoEditarManutencao

COLUNAS = ["Data", "Situação", "Problema relatado", "Responsável"]


class AbaManutencao(QWidget):
    def __init__(self, parent_ficha):
        super().__init__()
        self.parent_ficha = parent_ficha
        self.patrimonio_id: int | None = None
        self.registros: list[dict] = []
        self._montar_interface()

    def _montar_interface(self):
        layout = QVBoxLayout(self)

        linha_botoes = QHBoxLayout()
        self.botao_novo = QPushButton("REGISTRAR MANUTENÇÃO")
        self.botao_novo.clicked.connect(self._abrir_novo)
        linha_botoes.addWidget(self.botao_novo)
        linha_botoes.addStretch()
        layout.addLayout(linha_botoes)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(len(COLUNAS))
        self.tabela.setHorizontalHeaderLabels(COLUNAS)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabela.doubleClicked.connect(self._editar_selecionada)
        layout.addWidget(self.tabela)

    def carregar(self, patrimonio_id: int):
        self.patrimonio_id = patrimonio_id
        try:
            self.registros = cliente_api.listar_manutencoes(patrimonio_id)
        except (ErroAPI, ErroConexao) as erro:
            QMessageBox.warning(self, "Erro ao carregar manutenções", str(erro))
            self.registros = []

        self.tabela.setRowCount(len(self.registros))
        for linha, m in enumerate(self.registros):
            problema = (m.get("problema_relatado") or "—")
            problema_curto = problema if len(problema) <= 80 else problema[:77] + "..."
            valores = [m["data"], m["situacao"], problema_curto, m.get("responsavel_nome") or "—"]
            for coluna, texto in enumerate(valores):
                item = QTableWidgetItem(texto)
                if coluna == 0:
                    item.setData(Qt.UserRole, m["id"])
                self.tabela.setItem(linha, coluna, item)

    def _abrir_novo(self):
        if self.patrimonio_id is None:
            return
        dialogo = DialogoNovaManutencao(self.patrimonio_id, parent=self)
        if dialogo.exec():
            self.carregar(self.patrimonio_id)

    def _editar_selecionada(self):
        linha = self.tabela.currentRow()
        if linha < 0 or linha >= len(self.registros):
            return
        registro = self.registros[linha]
        dialogo = DialogoEditarManutencao(self.patrimonio_id, registro, parent=self)
        if dialogo.exec():
            self.carregar(self.patrimonio_id)
