from PySide6.QtWidgets import (
    QWidget, QFormLayout, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton,
    QHBoxLayout, QGroupBox, QMessageBox
)

from app.api_client import cliente_api, ErroAPI, ErroConexao

SITUACOES = ("Em uso", "Disponível", "Em manutenção", "Em garantia", "Emprestado", "Baixado", "Descartado")


class AbaCadastro(QWidget):
    """
    Mostra os dados em modo leitura por padrão. O botão 'Editar cadastro' libera
    os campos para edição, conforme a especificação (seção 13).
    Emite via callback (on_alteracao_pendente) quando algo muda em modo edição,
    para a janela-mãe controlar o aviso de 'alterações não salvas' ao fechar.
    """

    def __init__(self, parent_ficha):
        super().__init__()
        self.parent_ficha = parent_ficha
        self.dados: dict = {}
        self.em_edicao = False
        self._listas_carregadas = False

        self._montar_interface()

    # ---------------------------------------------------------------- UI

    def _montar_interface(self):
        layout = QVBoxLayout(self)

        # --- Identificação ---
        grupo_id = QGroupBox("Identificação")
        self.form_id = QFormLayout(grupo_id)
        self.lbl_patrimonio = QLabel()
        self.combo_item = QComboBox()
        self.combo_item.setEnabled(False)  # equipamento não é editável após criação (sem campo correspondente no PatrimonioUpdate)
        self.campo_ipm = QLineEdit()
        self.campo_serie = QLineEdit()
        self.form_id.addRow("Patrimônio:", self.lbl_patrimonio)
        self.form_id.addRow("Equipamento:", self.combo_item)
        self.form_id.addRow("IPM:", self.campo_ipm)
        self.form_id.addRow("Número de série:", self.campo_serie)
        layout.addWidget(grupo_id)

        # --- Aquisição ---
        grupo_aquisicao = QGroupBox("Aquisição")
        self.form_aquisicao = QFormLayout(grupo_aquisicao)
        self.combo_empenho = QComboBox()
        self.combo_aquisicao = QComboBox()
        self.form_aquisicao.addRow("Empenho/NE:", self.combo_empenho)
        self.form_aquisicao.addRow("Aquisição (fornecedor/NF):", self.combo_aquisicao)
        layout.addWidget(grupo_aquisicao)

        # --- Localização atual ---
        grupo_local = QGroupBox("Localização atual")
        self.form_local = QFormLayout(grupo_local)
        self.combo_secretaria = QComboBox()
        self.combo_setor = QComboBox()
        self.combo_local = QComboBox()
        self.combo_situacao = QComboBox()
        self.combo_situacao.addItems(SITUACOES)
        self.form_local.addRow("Secretaria:", self.combo_secretaria)
        self.form_local.addRow("Setor:", self.combo_setor)
        self.form_local.addRow("Local:", self.combo_local)
        self.form_local.addRow("Situação atual:", self.combo_situacao)
        layout.addWidget(grupo_local)

        # --- Pendências (só leitura, calculadas pela API) ---
        self.lbl_pendencias = QLabel()
        self.lbl_pendencias.setWordWrap(True)
        layout.addWidget(self.lbl_pendencias)

        # --- Botões ---
        linha_botoes = QHBoxLayout()
        self.botao_editar = QPushButton("✏️ Editar cadastro")
        self.botao_editar.clicked.connect(self._entrar_modo_edicao)
        self.botao_salvar = QPushButton("Salvar")
        self.botao_salvar.clicked.connect(self._salvar)
        self.botao_salvar.setVisible(False)
        self.botao_cancelar = QPushButton("Cancelar edição")
        self.botao_cancelar.clicked.connect(self._cancelar_edicao)
        self.botao_cancelar.setVisible(False)
        linha_botoes.addWidget(self.botao_editar)
        linha_botoes.addWidget(self.botao_salvar)
        linha_botoes.addWidget(self.botao_cancelar)
        linha_botoes.addStretch()
        layout.addLayout(linha_botoes)
        layout.addStretch()

        self._definir_somente_leitura(True)

        self.combo_secretaria.currentIndexChanged.connect(self._ao_trocar_secretaria)
        self.combo_setor.currentIndexChanged.connect(self._ao_trocar_setor)

        for widget in (self.campo_ipm, self.campo_serie, self.combo_empenho,
                       self.combo_aquisicao, self.combo_secretaria, self.combo_setor,
                       self.combo_local, self.combo_situacao):
            if isinstance(widget, QLineEdit):
                widget.textChanged.connect(self._marcar_alterado)
            else:
                widget.currentIndexChanged.connect(self._marcar_alterado)

    def _definir_somente_leitura(self, somente_leitura: bool):
        # combo_item fica de fora de propósito: o equipamento vinculado não é editável
        # depois que o patrimônio existe (o backend não aceita isso em PatrimonioUpdate).
        for widget in (self.combo_empenho, self.combo_aquisicao,
                       self.combo_secretaria, self.combo_setor, self.combo_local, self.combo_situacao):
            widget.setEnabled(not somente_leitura)
        self.campo_ipm.setReadOnly(somente_leitura)
        self.campo_serie.setReadOnly(somente_leitura)

    # ---------------------------------------------------------- Carregamento

    def carregar(self, dados: dict):
        self.dados = dados
        self._carregar_listas_se_necessario()
        self._bloquear_sinais(True)

        self.lbl_patrimonio.setText(f"<b>{dados['numero_patrimonio']}</b>")
        self._selecionar_por_id(self.combo_item, dados.get("item_id"))
        self.campo_ipm.setText(dados.get("ipm") or "")
        self.campo_serie.setText(dados.get("numero_serie") or "")
        self._selecionar_por_id(self.combo_empenho, dados.get("empenho_id"))
        self._selecionar_por_id(self.combo_aquisicao, dados.get("aquisicao_id"))
        self._selecionar_por_id(self.combo_secretaria, dados.get("secretaria_id"))
        self._recarregar_setores(dados.get("secretaria_id"), selecionar=dados.get("setor_id"))
        self._recarregar_locais(dados.get("setor_id"), selecionar=dados.get("local_id"))
        self.combo_situacao.setCurrentText(dados.get("situacao_atual") or "Disponível")

        pendencias = dados.get("pendencias") or []
        if pendencias:
            icones = "\n".join(f"⚠ {p}" for p in pendencias)
            self.lbl_pendencias.setText(f"<b>🟡 Cadastro incompleto:</b><br>{icones.replace(chr(10), '<br>')}")
        else:
            self.lbl_pendencias.setText("<b>🟢 Cadastro completo</b>")

        self._bloquear_sinais(False)
        self.em_edicao = False
        self._definir_somente_leitura(True)
        self.botao_editar.setVisible(True)
        self.botao_salvar.setVisible(False)
        self.botao_cancelar.setVisible(False)

    def _carregar_listas_se_necessario(self):
        if self._listas_carregadas:
            return
        try:
            itens = cliente_api.listar_itens()
            empenhos = cliente_api.listar_empenhos()
            aquisicoes = cliente_api.listar_aquisicoes()
            secretarias = cliente_api.listar_secretarias()
        except (ErroAPI, ErroConexao) as erro:
            QMessageBox.warning(self, "Erro ao carregar listas", str(erro))
            return

        self.combo_item.clear()
        for item in itens:
            self.combo_item.addItem(item["descricao"], item["id"])

        self.combo_empenho.clear()
        self.combo_empenho.addItem("— nenhum —", None)
        for emp in empenhos:
            self.combo_empenho.addItem(f"{emp['numero']}/{emp['ano']}", emp["id"])

        self.combo_aquisicao.clear()
        self.combo_aquisicao.addItem("— nenhuma —", None)
        for aq in aquisicoes:
            rotulo = f"Aquisição #{aq['id']}" + (f" — NF {aq['nota_fiscal']}" if aq.get("nota_fiscal") else "")
            self.combo_aquisicao.addItem(rotulo, aq["id"])

        self.combo_secretaria.clear()
        self.combo_secretaria.addItem("— não informado —", None)
        for sec in secretarias:
            self.combo_secretaria.addItem(sec["nome"], sec["id"])

        self._listas_carregadas = True

    def _ao_trocar_secretaria(self):
        secretaria_id = self.combo_secretaria.currentData()
        self._recarregar_setores(secretaria_id)

    def _recarregar_setores(self, secretaria_id, selecionar=None):
        self.combo_setor.blockSignals(True)
        self.combo_setor.clear()
        self.combo_setor.addItem("— não informado —", None)
        if secretaria_id:
            try:
                for setor in cliente_api.listar_setores(secretaria_id):
                    self.combo_setor.addItem(setor["nome"], setor["id"])
            except (ErroAPI, ErroConexao) as erro:
                QMessageBox.warning(self, "Erro ao carregar setores", str(erro))
        self._selecionar_por_id(self.combo_setor, selecionar)
        self.combo_setor.blockSignals(False)
        self._recarregar_locais(self.combo_setor.currentData())

    def _ao_trocar_setor(self):
        self._recarregar_locais(self.combo_setor.currentData())

    def _recarregar_locais(self, setor_id, selecionar=None):
        self.combo_local.blockSignals(True)
        self.combo_local.clear()
        self.combo_local.addItem("— não informado —", None)
        if setor_id:
            try:
                for local in cliente_api.listar_locais(setor_id):
                    self.combo_local.addItem(local["nome"], local["id"])
            except (ErroAPI, ErroConexao) as erro:
                QMessageBox.warning(self, "Erro ao carregar locais", str(erro))
        self._selecionar_por_id(self.combo_local, selecionar)
        self.combo_local.blockSignals(False)

    @staticmethod
    def _selecionar_por_id(combo: QComboBox, valor_id):
        for i in range(combo.count()):
            if combo.itemData(i) == valor_id:
                combo.setCurrentIndex(i)
                return
        if combo.count() > 0:
            combo.setCurrentIndex(0)

    def _bloquear_sinais(self, bloquear: bool):
        for widget in (self.combo_item, self.combo_empenho, self.combo_aquisicao,
                       self.combo_secretaria, self.combo_setor, self.combo_local, self.combo_situacao):
            widget.blockSignals(bloquear)

    # ---------------------------------------------------------------- Edição

    def _entrar_modo_edicao(self):
        self.em_edicao = True
        self._definir_somente_leitura(False)
        self.botao_editar.setVisible(False)
        self.botao_salvar.setVisible(True)
        self.botao_cancelar.setVisible(True)

    def _cancelar_edicao(self):
        self.carregar(self.dados)  # recarrega os valores originais
        self.parent_ficha.marcar_sem_alteracoes()

    def _marcar_alterado(self):
        if self.em_edicao:
            self.parent_ficha.marcar_com_alteracoes()

    def _salvar(self):
        alteracoes = {
            "ipm": self.campo_ipm.text().strip() or None,
            "numero_serie": self.campo_serie.text().strip() or None,
            "empenho_id": self.combo_empenho.currentData(),
            "aquisicao_id": self.combo_aquisicao.currentData(),
            "secretaria_id": self.combo_secretaria.currentData(),
            "setor_id": self.combo_setor.currentData(),
            "local_id": self.combo_local.currentData(),
            "situacao_atual": self.combo_situacao.currentText(),
        }
        try:
            atualizado = cliente_api.atualizar_patrimonio(self.dados["id"], alteracoes)
        except ErroConexao as erro:
            QMessageBox.critical(self, "Erro de conexão", str(erro))
            return
        except ErroAPI as erro:
            QMessageBox.warning(self, "Não foi possível salvar", erro.mensagem)
            return

        self.carregar(atualizado)
        self.parent_ficha.marcar_sem_alteracoes()
        self.parent_ficha.atualizar_apos_salvar(atualizado)
