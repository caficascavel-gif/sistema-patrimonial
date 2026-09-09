from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QMessageBox, QLabel

from app.config import definir_url_api, obter_url_api


class DialogoConfigServidor(QDialog):
    """
    Mostrado na primeira execução (ou quando o usuário pedir para reconfigurar).
    Só grava o endereço da API — as credenciais do MySQL nunca passam pelo cliente.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuração do Servidor")
        self.setMinimumWidth(400)

        self.campo_url = QLineEdit(self)
        self.campo_url.setPlaceholderText("http://servidor:8000")
        self.campo_url.setText(obter_url_api() or "")

        botoes = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        botoes.accepted.connect(self._confirmar)
        botoes.rejected.connect(self.reject)

        layout = QFormLayout(self)
        layout.addRow(QLabel("Endereço da API do sistema (fornecido pelo suporte/TI):"))
        layout.addRow("Servidor:", self.campo_url)
        layout.addWidget(botoes)

    def _confirmar(self):
        url = self.campo_url.text().strip()
        if not url:
            QMessageBox.warning(self, "Campo obrigatório", "Informe o endereço do servidor.")
            return
        definir_url_api(url)
        self.accept()
