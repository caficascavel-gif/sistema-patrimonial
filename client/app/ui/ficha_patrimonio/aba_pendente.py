from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class AbaPendente(QWidget):
    """Usada pelas abas Histórico, Movimentações, Manutenção, Garantia, Anotações
    e Documentos até as Etapas 7, 8 e 9 implementarem cada uma de verdade."""

    def __init__(self, nome_aba: str, etapa_prevista: int):
        super().__init__()
        layout = QVBoxLayout(self)
        aviso = QLabel(f"A aba \"{nome_aba}\" será implementada na Etapa {etapa_prevista}.")
        aviso.setAlignment(Qt.AlignCenter)
        aviso.setStyleSheet("color: #888; font-style: italic;")
        layout.addStretch()
        layout.addWidget(aviso)
        layout.addStretch()
