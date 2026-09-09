from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QTextEdit, QDialogButtonBox, QMessageBox, QLabel

from app.api_client import cliente_api, ErroAPI, ErroConexao


class DialogoRetornoGarantia(QDialog):
    """
    Botão 'REGISTRAR RETORNO DA GARANTIA' (seção 17). O usuário só escolhe o
    destino — a movimentação Fornecedor -> destino é criada automaticamente pela API.
    """

    def __init__(self, patrimonio_id: int, garantia: dict, parent=None):
        super().__init__(parent)
        self.patrimonio_id = patrimonio_id
        self.garantia_id = garantia["id"]
        self.setWindowTitle(f"Retorno da Garantia #{self.garantia_id}")
        self.setMinimumWidth(420)

        self.campo_destino = QLineEdit()
        self.campo_destino.setPlaceholderText("ex: Engenharia Clínica, USF Guarujá…")
        self.campo_observacao = QTextEdit()
        self.campo_observacao.setFixedHeight(60)

        formulario = QFormLayout(self)
        formulario.addRow(QLabel(
            f"Origem: {garantia.get('fornecedor_nome') or 'Fornecedor'} (automático)"
        ))
        formulario.addRow("Destino:", self.campo_destino)
        formulario.addRow("Observação:", self.campo_observacao)

        botoes = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        botoes.button(QDialogButtonBox.Ok).setText("Confirmar retorno")
        botoes.accepted.connect(self._confirmar)
        botoes.rejected.connect(self.reject)
        formulario.addWidget(botoes)

    def _confirmar(self):
        destino = self.campo_destino.text().strip()
        if not destino:
            QMessageBox.warning(self, "Campo obrigatório", "Informe o destino do retorno.")
            return

        dados = {"destino": destino, "observacao": self.campo_observacao.toPlainText().strip() or None}
        try:
            cliente_api.registrar_retorno_garantia(self.patrimonio_id, self.garantia_id, dados)
        except ErroConexao as erro:
            QMessageBox.critical(self, "Erro de conexão", str(erro))
            return
        except ErroAPI as erro:
            QMessageBox.warning(self, "Não foi possível registrar o retorno", erro.mensagem)
            return
        self.accept()
