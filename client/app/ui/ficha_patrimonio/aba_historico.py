from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame

from app.api_client import cliente_api, ErroAPI, ErroConexao

ICONE_TIPO = {
    "Entrada": "📥", "Transferência": "🔁", "Empréstimo": "🤝",
    "Engenharia Clínica": "🔧", "Manutenção": "🛠️", "Garantia": "🛡️",
    "Retorno de garantia": "↩️", "Retorno de manutenção": "↩️",
    "Baixa": "📉", "Descarte": "🗑️", "Outros": "•",
}


class AbaHistorico(QWidget):
    """
    Linha do tempo completa do patrimônio (seção 14), somente leitura.
    Mostra exatamente as mesmas movimentações da aba Movimentações, só que
    no formato de histórico cronológico — nunca edita nem apaga nada.
    """

    def __init__(self, parent_ficha):
        super().__init__()
        self.parent_ficha = parent_ficha
        self._montar_interface()

    def _montar_interface(self):
        layout_externo = QVBoxLayout(self)
        self.area_rolagem = QScrollArea()
        self.area_rolagem.setWidgetResizable(True)
        self.conteudo = QWidget()
        self.layout_conteudo = QVBoxLayout(self.conteudo)
        self.layout_conteudo.addStretch()
        self.area_rolagem.setWidget(self.conteudo)
        layout_externo.addWidget(self.area_rolagem)

    def carregar(self, patrimonio_id: int):
        erro_ao_carregar = None
        try:
            movimentacoes = cliente_api.listar_movimentacoes(patrimonio_id)
        except (ErroAPI, ErroConexao) as erro:
            movimentacoes = []
            erro_ao_carregar = str(erro)

        # limpa a linha do tempo anterior
        while self.layout_conteudo.count():
            filho = self.layout_conteudo.takeAt(0)
            if filho.widget():
                filho.widget().deleteLater()

        if erro_ao_carregar:
            self.layout_conteudo.addWidget(QLabel(f"⚠ Não foi possível carregar o histórico: {erro_ao_carregar}"))
        elif not movimentacoes:
            self.layout_conteudo.addWidget(QLabel("Nenhuma movimentação registrada ainda."))
        else:
            for mov in movimentacoes:
                self.layout_conteudo.addWidget(self._criar_item_timeline(mov))

        self.layout_conteudo.addStretch()

    def _criar_item_timeline(self, mov: dict) -> QFrame:
        icone = ICONE_TIPO.get(mov["tipo"], "•")
        data = mov["data"].replace("T", " ")[:16]

        linhas = [f"<b>{data}</b>", f"● {icone} {mov['tipo']}"]
        if mov.get("origem"):
            linhas.append(f"Origem: {mov['origem']}")
        if mov.get("destino"):
            linhas.append(f"Destino: {mov['destino']}")
        if mov.get("motivo"):
            linhas.append(f"Motivo: {mov['motivo']}")
        if mov.get("responsavel_nome"):
            linhas.append(f"Responsável: {mov['responsavel_nome']}")

        rotulo = QLabel("<br>".join(linhas))
        rotulo.setWordWrap(True)

        moldura = QFrame()
        moldura.setFrameShape(QFrame.StyledPanel)
        layout = QVBoxLayout(moldura)
        layout.addWidget(rotulo)
        return moldura
