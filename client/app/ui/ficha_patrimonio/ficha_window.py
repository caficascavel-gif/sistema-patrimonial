from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget, QMessageBox
)

from app.api_client import cliente_api, ErroAPI, ErroConexao
from app.ui.ficha_patrimonio.aba_cadastro import AbaCadastro
from app.ui.ficha_patrimonio.aba_historico import AbaHistorico
from app.ui.ficha_patrimonio.aba_movimentacoes import AbaMovimentacoes
from app.ui.ficha_patrimonio.aba_manutencao import AbaManutencao
from app.ui.ficha_patrimonio.aba_garantia import AbaGarantia
from app.ui.ficha_patrimonio.aba_anotacoes import AbaAnotacoes
from app.ui.ficha_patrimonio.aba_documentos import AbaDocumentos

SITUACAO_ICONE = {
    "Em uso": "🟢", "Disponível": "🟢", "Em manutenção": "🟠",
    "Em garantia": "🟠", "Emprestado": "🔵", "Baixado": "⚪", "Descartado": "⚪",
}


class JanelaFichaPatrimonio(QDialog):
    """
    Ficha eletrônica completa do patrimônio (seção 9 da especificação).
    Abre como uma janela grande sobre a tela principal (que continua por trás),
    com suporte a minimizar/maximizar/fechar e navegação entre os resultados
    da pesquisa atual sem precisar fechar a ficha.
    """

    def __init__(self, lista_ids_resultado: list[int], indice_atual: int, parent=None):
        super().__init__(parent)
        # Habilita minimizar/maximizar/fechar como uma janela de verdade, não um popup simples.
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint
                             | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.resize(900, 700)

        self.lista_ids_resultado = lista_ids_resultado
        self.indice_atual = indice_atual
        self.tem_alteracoes_pendentes = False

        self._montar_interface()
        self._carregar_patrimonio_atual()

    # ------------------------------------------------------------------ UI

    def _montar_interface(self):
        layout = QVBoxLayout(self)

        # Cabeçalho
        cabecalho = QVBoxLayout()
        linha_topo = QHBoxLayout()
        self.lbl_titulo = QLabel()
        self.lbl_contador = QLabel()
        linha_topo.addWidget(self.lbl_titulo)
        linha_topo.addStretch()
        linha_topo.addWidget(self.lbl_contador)
        cabecalho.addLayout(linha_topo)

        self.lbl_situacao = QLabel()
        cabecalho.addWidget(self.lbl_situacao)

        linha_nav = QHBoxLayout()
        self.botao_anterior = QPushButton("← Anterior")
        self.botao_anterior.clicked.connect(self._ir_anterior)
        self.botao_proximo = QPushButton("Próximo →")
        self.botao_proximo.clicked.connect(self._ir_proximo)
        linha_nav.addWidget(self.botao_anterior)
        linha_nav.addWidget(self.botao_proximo)
        linha_nav.addStretch()
        cabecalho.addLayout(linha_nav)

        layout.addLayout(cabecalho)

        # Abas
        self.abas = QTabWidget()
        self.aba_cadastro = AbaCadastro(self)
        self.abas.addTab(self.aba_cadastro, "Cadastro")
        self.aba_historico = AbaHistorico(self)
        self.abas.addTab(self.aba_historico, "Histórico")
        self.aba_movimentacoes = AbaMovimentacoes(self)
        self.abas.addTab(self.aba_movimentacoes, "Movimentações")
        self.aba_manutencao = AbaManutencao(self)
        self.abas.addTab(self.aba_manutencao, "Manutenção")
        self.aba_garantia = AbaGarantia(self)
        self.abas.addTab(self.aba_garantia, "Garantia")
        self.aba_anotacoes = AbaAnotacoes(self)
        self.abas.addTab(self.aba_anotacoes, "Anotações")
        self.aba_documentos = AbaDocumentos(self)
        self.abas.addTab(self.aba_documentos, "Documentos")
        layout.addWidget(self.abas)

    # ------------------------------------------------------------ Navegação

    def _carregar_patrimonio_atual(self):
        patrimonio_id = self.lista_ids_resultado[self.indice_atual]
        try:
            dados = cliente_api.obter_patrimonio(patrimonio_id)
        except ErroConexao as erro:
            QMessageBox.critical(self, "Erro de conexão", str(erro))
            return
        except ErroAPI as erro:
            QMessageBox.warning(self, "Erro ao abrir ficha", erro.mensagem)
            return

        self._atualizar_cabecalho(dados)
        self.aba_cadastro.carregar(dados)
        self.aba_historico.carregar(dados["id"])
        self.aba_movimentacoes.carregar(dados["id"])
        self.aba_manutencao.carregar(dados["id"])
        self.aba_garantia.carregar(dados["id"])
        self.aba_anotacoes.carregar(dados["id"])
        self.aba_documentos.carregar(dados["id"])
        self.tem_alteracoes_pendentes = False

    def recarregar_historico(self):
        """Chamado pela aba Movimentações depois de registrar uma nova movimentação."""
        if self.aba_cadastro.dados:
            self.aba_historico.carregar(self.aba_cadastro.dados["id"])

    def _atualizar_cabecalho(self, dados: dict):
        total = len(self.lista_ids_resultado)
        self.setWindowTitle(f"Patrimônio {dados['numero_patrimonio']}")
        self.lbl_titulo.setText(
            f"<span style='font-size:16pt;font-weight:bold;'>PATRIMÔNIO {dados['numero_patrimonio']}</span>"
            f"<br><span style='font-size:12pt;'>{(dados.get('item_descricao') or '—').upper()}</span>"
        )
        self.lbl_contador.setText(f"{self.indice_atual + 1} de {total}")
        icone = SITUACAO_ICONE.get(dados.get("situacao_atual", ""), "")
        self.lbl_situacao.setText(f"{icone} {dados.get('situacao_atual', '')}")

        self.botao_anterior.setEnabled(self.indice_atual > 0)
        self.botao_proximo.setEnabled(self.indice_atual < total - 1)

    def _ir_anterior(self):
        if self.indice_atual == 0:
            return
        if not self._confirmar_descarte_se_necessario():
            return
        self.indice_atual -= 1
        self._carregar_patrimonio_atual()

    def _ir_proximo(self):
        if self.indice_atual >= len(self.lista_ids_resultado) - 1:
            return
        if not self._confirmar_descarte_se_necessario():
            return
        self.indice_atual += 1
        self._carregar_patrimonio_atual()

    def atualizar_apos_salvar(self, dados_atualizados: dict):
        """Chamado pela aba Cadastro depois de salvar com sucesso, para atualizar o cabeçalho."""
        self._atualizar_cabecalho(dados_atualizados)

    # ------------------------------------------------------- Controle de "sujo"

    def marcar_com_alteracoes(self):
        self.tem_alteracoes_pendentes = True

    def marcar_sem_alteracoes(self):
        self.tem_alteracoes_pendentes = False

    def _confirmar_descarte_se_necessario(self) -> bool:
        """
        Implementa o aviso da seção 9: 'Existem alterações não salvas. Deseja
        salvar antes de fechar?' com Salvar / Não salvar / Cancelar.
        Retorna True se pode prosseguir (fechar/navegar), False se deve permanecer.
        """
        if not self.tem_alteracoes_pendentes:
            return True

        caixa = QMessageBox(self)
        caixa.setWindowTitle("Alterações não salvas")
        caixa.setText("Existem alterações não salvas. Deseja salvar antes de continuar?")
        botao_salvar = caixa.addButton("Salvar", QMessageBox.AcceptRole)
        botao_nao_salvar = caixa.addButton("Não salvar", QMessageBox.DestructiveRole)
        botao_cancelar = caixa.addButton("Cancelar", QMessageBox.RejectRole)
        caixa.exec()

        clicado = caixa.clickedButton()
        if clicado is botao_cancelar:
            return False
        if clicado is botao_salvar:
            self.aba_cadastro._salvar()
            return not self.tem_alteracoes_pendentes  # só prossegue se salvou de verdade
        if clicado is botao_nao_salvar:
            self.tem_alteracoes_pendentes = False
            return True
        return False

    def closeEvent(self, event):
        if self._confirmar_descarte_se_necessario():
            event.accept()
        else:
            event.ignore()
