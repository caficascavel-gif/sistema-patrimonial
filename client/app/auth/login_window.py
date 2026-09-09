from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QMessageBox, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
)

from app.api_client import cliente_api, ErroAPI, ErroConexao
from app.ui.dialogo_config_servidor import DialogoConfigServidor


class JanelaLogin(QDialog):
    """Login individual, conforme item 4 da especificação."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sistema de Controle Patrimonial — Login")
        self.setMinimumWidth(360)
        self.usuario_autenticado: dict | None = None

        self.campo_usuario = QLineEdit(self)
        self.campo_senha = QLineEdit(self)
        self.campo_senha.setEchoMode(QLineEdit.Password)
        self.campo_senha.returnPressed.connect(self._tentar_login)

        formulario = QFormLayout()
        formulario.addRow("Usuário:", self.campo_usuario)
        formulario.addRow("Senha:", self.campo_senha)

        botoes = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        botoes.button(QDialogButtonBox.Ok).setText("Entrar")
        botoes.accepted.connect(self._tentar_login)
        botoes.rejected.connect(self.reject)

        botao_config = QPushButton("Configurar servidor…", self)
        botao_config.clicked.connect(self._abrir_config_servidor)

        rodape = QHBoxLayout()
        rodape.addWidget(botao_config)
        rodape.addStretch()

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b>Controle Patrimonial — Secretaria Municipal de Saúde</b>"))
        layout.addLayout(formulario)
        layout.addWidget(botoes)
        layout.addLayout(rodape)

    def _abrir_config_servidor(self):
        DialogoConfigServidor(self).exec()

    def _tentar_login(self):
        usuario = self.campo_usuario.text().strip()
        senha = self.campo_senha.text()
        if not usuario or not senha:
            QMessageBox.warning(self, "Campos obrigatórios", "Informe usuário e senha.")
            return

        try:
            self.usuario_autenticado = cliente_api.login(usuario, senha)
        except ErroConexao as erro:
            QMessageBox.critical(self, "Erro de conexão", str(erro))
            return
        except ErroAPI as erro:
            if erro.status_code == 403:
                QMessageBox.warning(self, "Usuário inativo", erro.mensagem)
            else:
                QMessageBox.warning(self, "Falha no login", erro.mensagem)
            return

        self.accept()
