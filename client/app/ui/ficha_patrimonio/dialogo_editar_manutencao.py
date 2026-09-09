from PySide6.QtWidgets import QDialog, QFormLayout, QComboBox, QTextEdit, QDialogButtonBox, QMessageBox

from app.api_client import cliente_api, ErroAPI, ErroConexao

SITUACOES_MANUTENCAO = (
    "Em análise", "Em manutenção", "Aguardando peça", "Aguardando fornecedor",
    "Resolvido", "Sem conserto", "Encaminhado para garantia",
)


class DialogoEditarManutencao(QDialog):
    def __init__(self, patrimonio_id: int, manutencao: dict, parent=None):
        super().__init__(parent)
        self.patrimonio_id = patrimonio_id
        self.manutencao_id = manutencao["id"]
        self.setWindowTitle(f"Manutenção #{self.manutencao_id}")
        self.setMinimumWidth(420)

        self.combo_situacao = QComboBox()
        self.combo_situacao.addItems(SITUACOES_MANUTENCAO)
        self.combo_situacao.setCurrentText(manutencao.get("situacao") or "Em análise")

        self.campo_servico = QTextEdit(manutencao.get("servico_realizado") or "")
        self.campo_servico.setFixedHeight(60)
        self.campo_conclusao = QTextEdit(manutencao.get("conclusao") or "")
        self.campo_conclusao.setFixedHeight(60)

        formulario = QFormLayout(self)
        formulario.addRow("Situação:", self.combo_situacao)
        formulario.addRow("Serviço realizado:", self.campo_servico)
        formulario.addRow("Conclusão:", self.campo_conclusao)

        botoes = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        botoes.button(QDialogButtonBox.Ok).setText("Salvar")
        botoes.accepted.connect(self._salvar)
        botoes.rejected.connect(self.reject)
        formulario.addWidget(botoes)

    def _salvar(self):
        dados = {
            "situacao": self.combo_situacao.currentText(),
            "servico_realizado": self.campo_servico.toPlainText().strip() or None,
            "conclusao": self.campo_conclusao.toPlainText().strip() or None,
        }
        try:
            cliente_api.atualizar_manutencao(self.patrimonio_id, self.manutencao_id, dados)
        except ErroConexao as erro:
            QMessageBox.critical(self, "Erro de conexão", str(erro))
            return
        except ErroAPI as erro:
            QMessageBox.warning(self, "Não foi possível salvar", erro.mensagem)
            return
        self.accept()
