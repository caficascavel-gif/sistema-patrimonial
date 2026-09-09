from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QTextEdit, QDateEdit, QComboBox, QDialogButtonBox, QMessageBox
)

from app.api_client import cliente_api, ErroAPI, ErroConexao


class DialogoNovaGarantia(QDialog):
    def __init__(self, patrimonio_id: int, parent=None):
        super().__init__(parent)
        self.patrimonio_id = patrimonio_id
        self.setWindowTitle("Registrar Envio para Garantia")
        self.setMinimumWidth(420)

        self.combo_fornecedor = QComboBox()
        self._carregar_fornecedores()

        self.campo_protocolo = QLineEdit()
        self.campo_motivo = QLineEdit()
        self.campo_problema = QTextEdit()
        self.campo_problema.setFixedHeight(60)
        self.campo_data_envio = QDateEdit(QDate.currentDate())
        self.campo_data_envio.setCalendarPopup(True)
        self.campo_previsao = QDateEdit(QDate.currentDate().addDays(15))
        self.campo_previsao.setCalendarPopup(True)

        formulario = QFormLayout(self)
        formulario.addRow("Fornecedor:", self.combo_fornecedor)
        formulario.addRow("Protocolo:", self.campo_protocolo)
        formulario.addRow("Motivo:", self.campo_motivo)
        formulario.addRow("Problema:", self.campo_problema)
        formulario.addRow("Data de envio:", self.campo_data_envio)
        formulario.addRow("Previsão de retorno:", self.campo_previsao)

        botoes = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        botoes.button(QDialogButtonBox.Ok).setText("Registrar")
        botoes.accepted.connect(self._registrar)
        botoes.rejected.connect(self.reject)
        formulario.addWidget(botoes)

    def _carregar_fornecedores(self):
        self.combo_fornecedor.addItem("— não informado —", None)
        try:
            for f in cliente_api.listar_fornecedores():
                self.combo_fornecedor.addItem(f["razao_social"], f["id"])
        except (ErroAPI, ErroConexao) as erro:
            QMessageBox.warning(self, "Erro ao carregar fornecedores", str(erro))

    def _registrar(self):
        dados = {
            "fornecedor_id": self.combo_fornecedor.currentData(),
            "protocolo": self.campo_protocolo.text().strip() or None,
            "motivo": self.campo_motivo.text().strip() or None,
            "problema": self.campo_problema.toPlainText().strip() or None,
            "data_envio": self.campo_data_envio.date().toString("yyyy-MM-dd"),
            "previsao_retorno": self.campo_previsao.date().toString("yyyy-MM-dd"),
            "situacao": "Enviado",
        }
        try:
            cliente_api.criar_garantia(self.patrimonio_id, dados)
        except ErroConexao as erro:
            QMessageBox.critical(self, "Erro de conexão", str(erro))
            return
        except ErroAPI as erro:
            QMessageBox.warning(self, "Não foi possível registrar", erro.mensagem)
            return
        self.accept()
