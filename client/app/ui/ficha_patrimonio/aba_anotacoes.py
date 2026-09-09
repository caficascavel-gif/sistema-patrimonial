from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QScrollArea, QFrame, QMessageBox
)

from app.api_client import cliente_api, ErroAPI, ErroConexao


class AbaAnotacoes(QWidget):
    def __init__(self, parent_ficha):
        super().__init__()
        self.parent_ficha = parent_ficha
        self.patrimonio_id: int | None = None
        self._montar_interface()

    def _montar_interface(self):
        layout = QVBoxLayout(self)

        linha_nova = QHBoxLayout()
        self.campo_novo_texto = QTextEdit()
        self.campo_novo_texto.setFixedHeight(70)
        self.campo_novo_texto.setPlaceholderText("Escreva uma nova anotação…")
        botao_adicionar = QPushButton("+ NOVA ANOTAÇÃO")
        botao_adicionar.clicked.connect(self._adicionar)
        linha_nova.addWidget(self.campo_novo_texto)
        layout.addLayout(linha_nova)
        layout.addWidget(botao_adicionar)

        self.area_rolagem = QScrollArea()
        self.area_rolagem.setWidgetResizable(True)
        self.conteudo = QWidget()
        self.layout_conteudo = QVBoxLayout(self.conteudo)
        self.layout_conteudo.addStretch()
        self.area_rolagem.setWidget(self.conteudo)
        layout.addWidget(self.area_rolagem)

    def carregar(self, patrimonio_id: int):
        self.patrimonio_id = patrimonio_id
        try:
            anotacoes = cliente_api.listar_anotacoes(patrimonio_id)
        except (ErroAPI, ErroConexao):
            anotacoes = []

        while self.layout_conteudo.count():
            filho = self.layout_conteudo.takeAt(0)
            if filho.widget():
                filho.widget().deleteLater()

        if not anotacoes:
            self.layout_conteudo.addWidget(QLabel("Nenhuma anotação registrada ainda."))
        else:
            for nota in anotacoes:
                self.layout_conteudo.addWidget(self._criar_item(nota))
        self.layout_conteudo.addStretch()

    def _criar_item(self, nota: dict) -> QFrame:
        data = nota["data_hora"].replace("T", " ")[:16]
        rotulo = QLabel(f"<b>{data} — {nota.get('usuario_nome') or '—'}</b><br>{nota['texto']}")
        rotulo.setWordWrap(True)
        moldura = QFrame()
        moldura.setFrameShape(QFrame.StyledPanel)
        layout = QVBoxLayout(moldura)
        layout.addWidget(rotulo)
        return moldura

    def _adicionar(self):
        texto = self.campo_novo_texto.toPlainText().strip()
        if not texto:
            QMessageBox.warning(self, "Campo vazio", "Escreva o texto da anotação.")
            return
        try:
            cliente_api.criar_anotacao(self.patrimonio_id, texto)
        except ErroConexao as erro:
            QMessageBox.critical(self, "Erro de conexão", str(erro))
            return
        except ErroAPI as erro:
            QMessageBox.warning(self, "Não foi possível salvar", erro.mensagem)
            return
        self.campo_novo_texto.clear()
        self.carregar(self.patrimonio_id)
