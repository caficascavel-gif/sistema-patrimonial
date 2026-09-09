from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFrame, QMessageBox
)

from app.api_client import cliente_api, ErroAPI, ErroConexao
from app.ui.relatorios.tela_relatorio import TelaRelatorio

CARTOES_DASHBOARD = [
    ("total", "PATRIMÔNIOS"), ("em_uso", "EM USO"), ("em_manutencao", "MANUTENÇÃO"),
    ("em_garantia", "GARANTIA"), ("sem_local", "SEM LOCAL"), ("baixados", "BAIXADOS"),
]

PENDENCIAS_ROTULOS = [
    ("patrimonios_sem_fornecedor", "patrimônio(s) sem fornecedor"),
    ("patrimonios_sem_ne", "patrimônio(s) sem NE"),
    ("patrimonios_sem_localizacao", "patrimônio(s) sem localização"),
    ("patrimonios_sem_numero_serie", "patrimônio(s) sem número de série"),
    ("aquisicoes_sem_patrimonio", "aquisição(ões) sem patrimônio vinculado"),
]

COLUNAS_INCOMPLETOS = [
    ("numero_patrimonio", "Patrimônio"), ("equipamento", "Equipamento"),
    ("setor", "Setor"), ("local", "Local"), ("situacao", "Situação"),
    ("fornecedor", "Fornecedor"), ("ne", "NE"), ("pendencias", "Pendências"),
]


class JanelaDashboard(QDialog):
    """Tela inicial com indicadores (seção 26) e visão de pendências clicável (seção 24)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dashboard")
        self.resize(650, 450)
        self._montar_interface()
        self._carregar()

    def _montar_interface(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Indicadores</h2>"))

        self.grade_cartoes = QGridLayout()
        self.rotulos_cartoes = {}
        for indice, (chave, titulo) in enumerate(CARTOES_DASHBOARD):
            cartao = QFrame()
            cartao.setFrameShape(QFrame.StyledPanel)
            layout_cartao = QVBoxLayout(cartao)
            valor = QLabel("—")
            valor.setStyleSheet("font-size: 22pt; font-weight: bold;")
            rotulo = QLabel(titulo)
            layout_cartao.addWidget(valor)
            layout_cartao.addWidget(rotulo)
            self.rotulos_cartoes[chave] = valor
            self.grade_cartoes.addWidget(cartao, indice // 3, indice % 3)
        layout.addLayout(self.grade_cartoes)

        layout.addWidget(QLabel("<h2>Pendências</h2>"))
        self.layout_pendencias = QVBoxLayout()
        layout.addLayout(self.layout_pendencias)
        layout.addStretch()

    def _carregar(self):
        try:
            dados_dashboard = cliente_api.resumo_dashboard()
            dados_pendencias = cliente_api.resumo_pendencias()
        except (ErroAPI, ErroConexao) as erro:
            QMessageBox.warning(self, "Erro ao carregar dashboard", str(erro))
            return

        for chave, rotulo in self.rotulos_cartoes.items():
            rotulo.setText(str(dados_dashboard.get(chave, 0)))

        while self.layout_pendencias.count():
            filho = self.layout_pendencias.takeAt(0)
            if filho.widget():
                filho.widget().deleteLater()

        alguma_pendencia = False
        for chave, texto in PENDENCIAS_ROTULOS:
            quantidade = dados_pendencias.get(chave, 0)
            if quantidade > 0:
                alguma_pendencia = True
                botao = QPushButton(f"⚠ {quantidade} {texto}")
                botao.setStyleSheet("text-align: left;")
                botao.clicked.connect(lambda _=False: self._abrir_incompletos())
                self.layout_pendencias.addWidget(botao)

        if not alguma_pendencia:
            self.layout_pendencias.addWidget(QLabel("🟢 Nenhuma pendência encontrada."))

    def _abrir_incompletos(self):
        try:
            linhas = cliente_api.relatorio_incompletos()
        except (ErroAPI, ErroConexao) as erro:
            QMessageBox.warning(self, "Erro ao abrir pendências", str(erro))
            return
        tela = TelaRelatorio("Patrimônios sem informações completas", COLUNAS_INCOMPLETOS, linhas, parent=self)
        tela.exec()
