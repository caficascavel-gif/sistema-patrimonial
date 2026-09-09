from datetime import date

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QTextEdit, QDateEdit, QDialogButtonBox, QMessageBox
)
from PySide6.QtCore import QDate

from app.api_client import cliente_api, ErroAPI, ErroConexao


class DialogoNovaManutencao(QDialog):
    def __init__(self, patrimonio_id: int, parent=None):
        super().__init__(parent)
        self.patrimonio_id = patrimonio_id
        self.setWindowTitle("Registrar Manutenção")
        self.setMinimumWidth(420)

        self.campo_data = QDateEdit(QDate.currentDate())
        self.campo_data.setCalendarPopup(True)
        self.campo_problema = QTextEdit()
        self.campo_problema.setFixedHeight(70)
        self.campo_observacoes = QTextEdit()
        self.campo_observacoes.setFixedHeight(60)

        formulario = QFormLayout(self)
        formulario.addRow("Data:", self.campo_data)
        formulario.addRow("Problema relatado:", self.campo_problema)
        formulario.addRow("Observações:", self.campo_observacoes)

        botoes = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        botoes.button(QDialogButtonBox.Ok).setText("Registrar")
        botoes.accepted.connect(self._registrar)
        botoes.rejected.connect(self.reject)
        formulario.addWidget(botoes)

    def _registrar(self):
        dados = {
            "data": self.campo_data.date().toString("yyyy-MM-dd"),
            "problema_relatado": self.campo_problema.toPlainText().strip() or None,
            "observacoes": self.campo_observacoes.toPlainText().strip() or None,
        }
        try:
            cliente_api.criar_manutencao(self.patrimonio_id, dados)
        except ErroConexao as erro:
            QMessageBox.critical(self, "Erro de conexão", str(erro))
            return
        except ErroAPI as erro:
            QMessageBox.warning(self, "Não foi possível registrar", erro.mensagem)
            return
        self.accept()
