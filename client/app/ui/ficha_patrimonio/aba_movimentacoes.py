from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox
)

from app.api_client import cliente_api, ErroAPI, ErroConexao
from app.ui.ficha_patrimonio.dialogo_nova_movimentacao import DialogoNovaMovimentacao

COLUNAS = ["Data", "Tipo", "Origem", "Destino", "Responsável"]


class AbaMovimentacoes(QWidget):
    def __init__(self, parent_ficha):
        super().__init__()
        self.parent_ficha = parent_ficha
        self.patrimonio_id: int | None = None
        self.movimentacoes: list[dict] = []
        self._montar_interface()

    def _montar_interface(self):
        layout = QVBoxLayout(self)

        linha_botoes = QHBoxLayout()
        self.botao_nova = QPushButton("+ NOVA MOVIMENTAÇÃO")
        self.botao_nova.clicked.connect(self._abrir_dialogo_nova)
        linha_botoes.addWidget(self.botao_nova)
        linha_botoes.addStretch()
        layout.addLayout(linha_botoes)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(len(COLUNAS))
        self.tabela.setHorizontalHeaderLabels(COLUNAS)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabela.doubleClicked.connect(self._mostrar_detalhes)
        layout.addWidget(self.tabela)

    def carregar(self, patrimonio_id: int):
        self.patrimonio_id = patrimonio_id
        try:
            self.movimentacoes = cliente_api.listar_movimentacoes(patrimonio_id)
        except (ErroAPI, ErroConexao) as erro:
            QMessageBox.warning(self, "Erro ao carregar movimentações", str(erro))
            self.movimentacoes = []

        self.tabela.setRowCount(len(self.movimentacoes))
        for linha, mov in enumerate(self.movimentacoes):
            data_formatada = mov["data"].replace("T", " ")[:16]
            valores = [data_formatada, mov["tipo"], mov.get("origem") or "—",
                       mov.get("destino") or "—", mov.get("responsavel_nome") or "—"]
            for coluna, texto in enumerate(valores):
                item = QTableWidgetItem(texto)
                if coluna == 0:
                    item.setData(Qt.UserRole, mov["id"])
                self.tabela.setItem(linha, coluna, item)

    def _abrir_dialogo_nova(self):
        if self.patrimonio_id is None:
            return
        dialogo = DialogoNovaMovimentacao(self.patrimonio_id, parent=self)
        if dialogo.exec():
            self.carregar(self.patrimonio_id)
            self.parent_ficha.recarregar_historico()

    def _mostrar_detalhes(self):
        linha = self.tabela.currentRow()
        if linha < 0 or linha >= len(self.movimentacoes):
            return
        mov = self.movimentacoes[linha]
        texto = (
            f"Data: {mov['data'].replace('T', ' ')[:16]}\n"
            f"Tipo: {mov['tipo']}\n"
            f"Origem: {mov.get('origem') or '—'}\n"
            f"Destino: {mov.get('destino') or '—'}\n"
            f"Responsável: {mov.get('responsavel_nome') or '—'}\n"
            f"Motivo: {mov.get('motivo') or '—'}\n\n"
            f"Observação:\n{mov.get('observacao') or '—'}"
        )
        QMessageBox.information(self, f"Movimentação #{mov['id']}", texto)
