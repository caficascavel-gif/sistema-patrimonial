from PySide6.QtWidgets import (
    QDialog, QFormLayout, QComboBox, QLineEdit, QTextEdit, QDialogButtonBox, QMessageBox
)

from app.api_client import cliente_api, ErroAPI, ErroConexao

TIPOS_MOVIMENTACAO = (
    "Entrada", "Transferência", "Empréstimo", "Engenharia Clínica",
    "Manutenção", "Garantia", "Retorno de garantia", "Retorno de manutenção",
    "Baixa", "Descarte", "Outros",
)


class DialogoNovaMovimentacao(QDialog):
    def __init__(self, patrimonio_id: int, parent=None):
        super().__init__(parent)
        self.patrimonio_id = patrimonio_id
        self.setWindowTitle("Nova Movimentação")
        self.setMinimumWidth(420)

        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(TIPOS_MOVIMENTACAO)
        self.campo_origem = QLineEdit()
        self.campo_destino = QLineEdit()
        self.campo_motivo = QLineEdit()
        self.campo_observacao = QTextEdit()
        self.campo_observacao.setFixedHeight(80)

        formulario = QFormLayout(self)
        formulario.addRow("Tipo:", self.combo_tipo)
        formulario.addRow("Origem:", self.campo_origem)
        formulario.addRow("Destino:", self.campo_destino)
        formulario.addRow("Motivo:", self.campo_motivo)
        formulario.addRow("Observação:", self.campo_observacao)

        botoes = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        botoes.button(QDialogButtonBox.Ok).setText("Registrar")
        botoes.accepted.connect(self._registrar)
        botoes.rejected.connect(self.reject)
        formulario.addWidget(botoes)

    def _registrar(self):
        dados = {
            "tipo": self.combo_tipo.currentText(),
            "origem": self.campo_origem.text().strip() or None,
            "destino": self.campo_destino.text().strip() or None,
            "motivo": self.campo_motivo.text().strip() or None,
            "observacao": self.campo_observacao.toPlainText().strip() or None,
        }
        try:
            cliente_api.criar_movimentacao(self.patrimonio_id, dados)
        except ErroConexao as erro:
            QMessageBox.critical(self, "Erro de conexão", str(erro))
            return
        except ErroAPI as erro:
            QMessageBox.warning(self, "Não foi possível registrar", erro.mensagem)
            return
        self.accept()
