import sys

from PySide6.QtWidgets import QApplication, QDialog

from app.api_client import cliente_api
from app.auth.login_window import JanelaLogin
from app.config import obter_url_api
from app.ui.dialogo_config_servidor import DialogoConfigServidor
from app.ui.main_window import JanelaPrincipal


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Sistema de Controle Patrimonial")

    # Primeira execução: pede o endereço do servidor antes de qualquer outra coisa.
    if not obter_url_api():
        dialogo = DialogoConfigServidor()
        if dialogo.exec() != QDialog.Accepted:
            sys.exit(0)

    janela_login = JanelaLogin()
    if janela_login.exec() != QDialog.Accepted:
        sys.exit(0)

    janela_principal = JanelaPrincipal(usuario_logado=cliente_api.usuario_logado)
    janela_principal.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
