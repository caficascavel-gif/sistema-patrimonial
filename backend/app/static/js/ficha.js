let _fichaListaIds = [];
let _fichaIndiceAtual = 0;
let _fichaDados = null;
let _fichaAbaAtiva = "cadastro";
let _fichaEmEdicao = false;
let _fichaAlteracoesPendentes = false;
let _fichaListasAuxiliares = null; // cache de itens/empenhos/aquisicoes/secretarias

function inicializarFicha() {
  document.getElementById("ficha-anterior").addEventListener("click", () => navegarFicha(-1));
  document.getElementById("ficha-proximo").addEventListener("click", () => navegarFicha(1));
  document.getElementById("ficha-fechar").addEventListener("click", fecharFicha);
  document.querySelectorAll(".aba-botao").forEach((botao) => {
    botao.addEventListener("click", () => trocarAba(botao.dataset.aba));
  });
}

function abrirFicha(listaResultados, indice) {
  _fichaListaIds = listaResultados.map((p) => p.id);
  _fichaIndiceAtual = indice;
  _fichaAbaAtiva = "cadastro";
  _fichaEmEdicao = false;
  _fichaAlteracoesPendentes = false;
  document.getElementById("modal-ficha").classList.remove("oculto");
  carregarFichaAtual();
}

function confirmarDescarteSeNecessario() {
  if (!_fichaAlteracoesPendentes) return true;
  return confirm("Existem alterações não salvas. Deseja descartar e continuar?");
}

function fecharFicha() {
  if (!confirmarDescarteSeNecessario()) return;
  document.getElementById("modal-ficha").classList.add("oculto");
}

function navegarFicha(delta) {
  if (!confirmarDescarteSeNecessario()) return;
  const novoIndice = _fichaIndiceAtual + delta;
  if (novoIndice < 0 || novoIndice >= _fichaListaIds.length) return;
  _fichaIndiceAtual = novoIndice;
  _fichaEmEdicao = false;
  _fichaAlteracoesPendentes = false;
  carregarFichaAtual();
}

async function carregarFichaAtual() {
  const id = _fichaListaIds[_fichaIndiceAtual];
  try {
    _fichaDados = await ClienteAPI.obterPatrimonio(id);
  } catch (e) {
    alert("Erro ao abrir ficha: " + e.message);
    return;
  }
  atualizarCabecalhoFicha();
  trocarAba(_fichaAbaAtiva);
}

function atualizarCabecalhoFicha() {
  const total = _fichaListaIds.length;
  document.getElementById("ficha-titulo").textContent =
    `PATRIMÔNIO ${_fichaDados.numero_patrimonio} — ${_fichaDados.item_descricao || "—"}`;
  document.getElementById("ficha-situacao").textContent =
    `${iconeSituacao(_fichaDados.situacao_atual)} ${_fichaDados.situacao_atual}`;
  document.getElementById("ficha-contador").textContent = `${_fichaIndiceAtual + 1} de ${total}`;
  document.getElementById("ficha-anterior").disabled = _fichaIndiceAtual === 0;
  document.getElementById("ficha-proximo").disabled = _fichaIndiceAtual === total - 1;
}

function trocarAba(nomeAba) {
  if (_fichaAbaAtiva !== nomeAba && !confirmarDescarteSeNecessario()) return;
  _fichaAbaAtiva = nomeAba;
  _fichaEmEdicao = false;
  _fichaAlteracoesPendentes = false;
  document.querySelectorAll(".aba-botao").forEach((b) => b.classList.toggle("ativa", b.dataset.aba === nomeAba));

  const funcoes = {
    cadastro: renderizarAbaCadastro,
    historico: renderizarAbaHistorico,
    movimentacoes: renderizarAbaMovimentacoes,
    manutencao: renderizarAbaManutencao,
    garantia: renderizarAbaGarantia,
    anotacoes: renderizarAbaAnotacoes,
    documentos: renderizarAbaDocumentos,
  };
  funcoes[nomeAba]();
}

// Nota: não existe um "recarregar histórico manualmente" aqui — a aba
// Histórico sempre busca os dados de novo sozinha ao ser aberta (trocarAba
// chama renderizarAbaHistorico do zero), então uma movimentação nova ou um
// retorno de garantia automático já aparecem certinhos na próxima vez que
// a pessoa clicar na aba Histórico, sem precisar de nenhum gatilho especial.

// ================================================================ CADASTRO

async function carregarListasAuxiliares() {
  if (_fichaListasAuxiliares) return _fichaListasAuxiliares;
  const [itens, empenhos, aquisicoes, secretarias] = await Promise.all([
    ClienteAPI.listarItens(), ClienteAPI.listarEmpenhos(),
    ClienteAPI.listarAquisicoes(), ClienteAPI.listarSecretarias(),
  ]);
  _fichaListasAuxiliares = { itens, empenhos, aquisicoes, secretarias };
  return _fichaListasAuxiliares;
}

function renderizarAbaCadastro() {
  const corpo = document.getElementById("ficha-corpo");
  const d = _fichaDados;
  const pendencias = d.pendencias || [];
  const blocoPendencias = pendencias.length
    ? `<p><b>🟡 Cadastro incompleto:</b><br>${pendencias.map((p) => `⚠ ${escaparHtml(p)}`).join("<br>")}</p>`
    : `<p><b>🟢 Cadastro completo</b></p>`;

  if (!_fichaEmEdicao) {
    corpo.innerHTML = `
      <h3>Identificação</h3>
      <p>Patrimônio: <b>${escaparHtml(d.numero_patrimonio)}</b><br>
         Equipamento: ${escaparHtml(d.item_descricao || "—")}<br>
         IPM: ${escaparHtml(d.ipm || "—")}<br>
         Número de série: ${escaparHtml(d.numero_serie || "—")}</p>
      <h3>Localização atual</h3>
      <p>Local: ${escaparHtml(d.local_descricao || "—")}<br>
         Situação: ${iconeSituacao(d.situacao_atual)} ${escaparHtml(d.situacao_atual)}</p>
      ${blocoPendencias}
      <button id="botao-editar-cadastro">✏️ Editar cadastro</button>
    `;
    document.getElementById("botao-editar-cadastro").addEventListener("click", () => {
      _fichaEmEdicao = true;
      renderizarAbaCadastro();
    });
    return;
  }

  // ---- modo edição ----
  corpo.innerHTML = `<p class="mensagem-info">Carregando formulário…</p>`;
  carregarListasAuxiliares().then(async ({ itens, empenhos, aquisicoes, secretarias }) => {
    const setores = d.secretaria_id ? await ClienteAPI.listarSetores(d.secretaria_id) : [];
    const locais = d.setor_id ? await ClienteAPI.listarLocais(d.setor_id) : [];

    corpo.innerHTML = `
      <div class="grupo-form"><label>IPM</label><input id="edit-ipm" value="${escaparHtml(d.ipm || "")}"></div>
      <div class="grupo-form" style="margin-top:8px;"><label>Número de série</label><input id="edit-serie" value="${escaparHtml(d.numero_serie || "")}"></div>
      <div class="grupo-form" style="margin-top:8px;"><label>Empenho/NE</label><select id="edit-empenho"></select></div>
      <div class="grupo-form" style="margin-top:8px;"><label>Aquisição</label><select id="edit-aquisicao"></select></div>
      <div class="grupo-form" style="margin-top:8px;"><label>Secretaria</label><select id="edit-secretaria"></select></div>
      <div class="grupo-form" style="margin-top:8px;"><label>Setor</label><select id="edit-setor"></select></div>
      <div class="grupo-form" style="margin-top:8px;"><label>Local</label><select id="edit-local"></select></div>
      <div class="grupo-form" style="margin-top:8px;"><label>Situação</label><select id="edit-situacao"></select></div>
      <div style="margin-top:16px;">
        <button id="botao-salvar-cadastro">Salvar</button>
        <button class="secundario" id="botao-cancelar-cadastro">Cancelar</button>
      </div>
    `;

    preencherSelect(document.getElementById("edit-empenho"), empenhos.map((e) => ({ id: e.id, nome: `${e.numero}/${e.ano}` })), { vazio: "— nenhum —" });
    preencherSelect(document.getElementById("edit-aquisicao"), aquisicoes.map((a) => ({ id: a.id, nome: `Aquisição #${a.id}${a.nota_fiscal ? " — NF " + a.nota_fiscal : ""}` })), { vazio: "— nenhuma —" });
    preencherSelect(document.getElementById("edit-secretaria"), secretarias, { vazio: "— não informado —" });
    preencherSelect(document.getElementById("edit-setor"), setores, { vazio: "— não informado —" });
    preencherSelect(document.getElementById("edit-local"), locais, { vazio: "— não informado —" });
    preencherSelect(document.getElementById("edit-situacao"), SITUACOES_PATRIMONIO.map((s) => ({ id: s, nome: s })));

    document.getElementById("edit-empenho").value = d.empenho_id || "";
    document.getElementById("edit-aquisicao").value = d.aquisicao_id || "";
    document.getElementById("edit-secretaria").value = d.secretaria_id || "";
    document.getElementById("edit-setor").value = d.setor_id || "";
    document.getElementById("edit-local").value = d.local_id || "";
    document.getElementById("edit-situacao").value = d.situacao_atual;

    document.getElementById("edit-secretaria").addEventListener("change", async (e) => {
      const novosSetores = e.target.value ? await ClienteAPI.listarSetores(parseInt(e.target.value, 10)) : [];
      preencherSelect(document.getElementById("edit-setor"), novosSetores, { vazio: "— não informado —" });
      preencherSelect(document.getElementById("edit-local"), [], { vazio: "— não informado —" });
    });
    document.getElementById("edit-setor").addEventListener("change", async (e) => {
      const novosLocais = e.target.value ? await ClienteAPI.listarLocais(parseInt(e.target.value, 10)) : [];
      preencherSelect(document.getElementById("edit-local"), novosLocais, { vazio: "— não informado —" });
    });

    corpo.querySelectorAll("input, select").forEach((campo) => {
      campo.addEventListener("input", () => { _fichaAlteracoesPendentes = true; });
      campo.addEventListener("change", () => { _fichaAlteracoesPendentes = true; });
    });

    document.getElementById("botao-cancelar-cadastro").addEventListener("click", () => {
      _fichaEmEdicao = false;
      _fichaAlteracoesPendentes = false;
      renderizarAbaCadastro();
    });

    document.getElementById("botao-salvar-cadastro").addEventListener("click", async () => {
      const alteracoes = {
        ipm: document.getElementById("edit-ipm").value.trim() || null,
        numero_serie: document.getElementById("edit-serie").value.trim() || null,
        empenho_id: document.getElementById("edit-empenho").value ? parseInt(document.getElementById("edit-empenho").value, 10) : null,
        aquisicao_id: document.getElementById("edit-aquisicao").value ? parseInt(document.getElementById("edit-aquisicao").value, 10) : null,
        secretaria_id: document.getElementById("edit-secretaria").value ? parseInt(document.getElementById("edit-secretaria").value, 10) : null,
        setor_id: document.getElementById("edit-setor").value ? parseInt(document.getElementById("edit-setor").value, 10) : null,
        local_id: document.getElementById("edit-local").value ? parseInt(document.getElementById("edit-local").value, 10) : null,
        situacao_atual: document.getElementById("edit-situacao").value,
      };
      try {
        _fichaDados = await ClienteAPI.atualizarPatrimonio(d.id, alteracoes);
      } catch (e) {
        alert("Não foi possível salvar: " + e.message);
        return;
      }
      _fichaEmEdicao = false;
      _fichaAlteracoesPendentes = false;
      atualizarCabecalhoFicha();
      renderizarAbaCadastro();
    });
  });
}

// ================================================================ HISTÓRICO

async function renderizarAbaHistorico() {
  const corpo = document.getElementById("ficha-corpo");
  corpo.innerHTML = `<p class="mensagem-info">Carregando…</p>`;
  let movimentacoes;
  try {
    movimentacoes = await ClienteAPI.listarMovimentacoes(_fichaDados.id);
  } catch (e) {
    corpo.innerHTML = `<p class="mensagem-erro">Não foi possível carregar o histórico: ${escaparHtml(e.message)}</p>`;
    return;
  }
  if (movimentacoes.length === 0) {
    corpo.innerHTML = `<p class="mensagem-info">Nenhuma movimentação registrada ainda.</p>`;
    return;
  }
  corpo.innerHTML = movimentacoes.map((m) => `
    <div class="timeline-item">
      <b>${formatarDataHora(m.data)}</b><br>
      ● ${escaparHtml(m.tipo)}<br>
      ${m.origem ? `Origem: ${escaparHtml(m.origem)}<br>` : ""}
      ${m.destino ? `Destino: ${escaparHtml(m.destino)}<br>` : ""}
      ${m.motivo ? `Motivo: ${escaparHtml(m.motivo)}<br>` : ""}
      Responsável: ${escaparHtml(m.responsavel_nome || "—")}
    </div>
  `).join("");
}

// ============================================================ MOVIMENTAÇÕES

async function renderizarAbaMovimentacoes() {
  const corpo = document.getElementById("ficha-corpo");
  corpo.innerHTML = `
    <button id="botao-nova-movimentacao">+ NOVA MOVIMENTAÇÃO</button>
    <table style="margin-top:12px;">
      <thead><tr><th>Data</th><th>Tipo</th><th>Origem</th><th>Destino</th><th>Responsável</th></tr></thead>
      <tbody id="tabela-movimentacoes"></tbody>
    </table>
  `;
  document.getElementById("botao-nova-movimentacao").addEventListener("click", abrirDialogoNovaMovimentacao);
  await carregarTabelaMovimentacoes();
}

async function carregarTabelaMovimentacoes() {
  const tbody = document.getElementById("tabela-movimentacoes");
  let movimentacoes;
  try {
    movimentacoes = await ClienteAPI.listarMovimentacoes(_fichaDados.id);
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="5" class="mensagem-erro">${escaparHtml(e.message)}</td></tr>`;
    return;
  }
  tbody.innerHTML = movimentacoes.map((m) => `
    <tr><td>${formatarDataHora(m.data)}</td><td>${escaparHtml(m.tipo)}</td>
        <td>${escaparHtml(m.origem || "—")}</td><td>${escaparHtml(m.destino || "—")}</td>
        <td>${escaparHtml(m.responsavel_nome || "—")}</td></tr>
  `).join("");
}

function abrirDialogoNovaMovimentacao() {
  const opcoesTipos = TIPOS_MOVIMENTACAO.map((t) => `<option value="${t}">${t}</option>`).join("");
  const html = `
    <div class="grupo-form"><label>Tipo</label><select id="dlg-mov-tipo">${opcoesTipos}</select></div>
    <div class="grupo-form" style="margin-top:8px;"><label>Origem</label><input id="dlg-mov-origem"></div>
    <div class="grupo-form" style="margin-top:8px;"><label>Destino</label><input id="dlg-mov-destino"></div>
    <div class="grupo-form" style="margin-top:8px;"><label>Motivo</label><input id="dlg-mov-motivo"></div>
    <div class="grupo-form" style="margin-top:8px;"><label>Observação</label><textarea id="dlg-mov-obs" rows="3"></textarea></div>
  `;
  abrirDialogoGenerico("Nova Movimentação", html, async () => {
    const dados = {
      tipo: document.getElementById("dlg-mov-tipo").value,
      origem: document.getElementById("dlg-mov-origem").value.trim() || null,
      destino: document.getElementById("dlg-mov-destino").value.trim() || null,
      motivo: document.getElementById("dlg-mov-motivo").value.trim() || null,
      observacao: document.getElementById("dlg-mov-obs").value.trim() || null,
    };
    await ClienteAPI.criarMovimentacao(_fichaDados.id, dados);
    await carregarTabelaMovimentacoes();
  });
}

// =============================================================== MANUTENÇÃO

async function renderizarAbaManutencao() {
  const corpo = document.getElementById("ficha-corpo");
  corpo.innerHTML = `
    <button id="botao-nova-manutencao">REGISTRAR MANUTENÇÃO</button>
    <table style="margin-top:12px;">
      <thead><tr><th>Data</th><th>Situação</th><th>Problema relatado</th><th>Responsável</th></tr></thead>
      <tbody id="tabela-manutencao"></tbody>
    </table>
  `;
  document.getElementById("botao-nova-manutencao").addEventListener("click", abrirDialogoNovaManutencao);
  await carregarTabelaManutencao();
}

async function carregarTabelaManutencao() {
  const tbody = document.getElementById("tabela-manutencao");
  let registros;
  try {
    registros = await ClienteAPI.listarManutencoes(_fichaDados.id);
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="4" class="mensagem-erro">${escaparHtml(e.message)}</td></tr>`;
    return;
  }
  tbody.innerHTML = registros.map((m) => `
    <tr class="clicavel" data-id="${m.id}">
      <td>${escaparHtml(m.data)}</td><td>${escaparHtml(m.situacao)}</td>
      <td>${escaparHtml((m.problema_relatado || "—").slice(0, 80))}</td>
      <td>${escaparHtml(m.responsavel_nome || "—")}</td>
    </tr>
  `).join("");
  tbody.querySelectorAll("tr").forEach((linha) => {
    linha.addEventListener("click", () => {
      const registro = registros.find((r) => r.id === parseInt(linha.dataset.id, 10));
      abrirDialogoEditarManutencao(registro);
    });
  });
}

function abrirDialogoNovaManutencao() {
  const html = `
    <div class="grupo-form"><label>Data</label><input type="date" id="dlg-man-data" value="${new Date().toISOString().slice(0, 10)}"></div>
    <div class="grupo-form" style="margin-top:8px;"><label>Problema relatado</label><textarea id="dlg-man-problema" rows="3"></textarea></div>
  `;
  abrirDialogoGenerico("Registrar Manutenção", html, async () => {
    const dados = {
      data: document.getElementById("dlg-man-data").value,
      problema_relatado: document.getElementById("dlg-man-problema").value.trim() || null,
    };
    await ClienteAPI.criarManutencao(_fichaDados.id, dados);
    await carregarTabelaManutencao();
  });
}

function abrirDialogoEditarManutencao(registro) {
  const opcoes = SITUACOES_MANUTENCAO.map((s) => `<option value="${s}" ${s === registro.situacao ? "selected" : ""}>${s}</option>`).join("");
  const html = `
    <div class="grupo-form"><label>Situação</label><select id="dlg-man2-situacao">${opcoes}</select></div>
    <div class="grupo-form" style="margin-top:8px;"><label>Serviço realizado</label><textarea id="dlg-man2-servico" rows="2">${escaparHtml(registro.servico_realizado || "")}</textarea></div>
    <div class="grupo-form" style="margin-top:8px;"><label>Conclusão</label><textarea id="dlg-man2-conclusao" rows="2">${escaparHtml(registro.conclusao || "")}</textarea></div>
  `;
  abrirDialogoGenerico(`Manutenção #${registro.id}`, html, async () => {
    const dados = {
      situacao: document.getElementById("dlg-man2-situacao").value,
      servico_realizado: document.getElementById("dlg-man2-servico").value.trim() || null,
      conclusao: document.getElementById("dlg-man2-conclusao").value.trim() || null,
    };
    await ClienteAPI.atualizarManutencao(_fichaDados.id, registro.id, dados);
    await carregarTabelaManutencao();
  }, "Salvar");
}

// ================================================================= GARANTIA

async function renderizarAbaGarantia() {
  const corpo = document.getElementById("ficha-corpo");
  corpo.innerHTML = `
    <button id="botao-nova-garantia">Registrar envio para garantia</button>
    <button class="secundario" id="botao-retorno-garantia" disabled>REGISTRAR RETORNO DA GARANTIA</button>
    <table style="margin-top:12px;">
      <thead><tr><th>Fornecedor</th><th>Protocolo</th><th>Situação</th><th>Previsão de retorno</th></tr></thead>
      <tbody id="tabela-garantia"></tbody>
    </table>
  `;
  document.getElementById("botao-nova-garantia").addEventListener("click", abrirDialogoNovaGarantia);
  await carregarTabelaGarantia();
}

async function carregarTabelaGarantia() {
  const tbody = document.getElementById("tabela-garantia");
  const botaoRetorno = document.getElementById("botao-retorno-garantia");
  botaoRetorno.disabled = true;
  botaoRetorno.onclick = null;

  let registros;
  try {
    registros = await ClienteAPI.listarGarantias(_fichaDados.id);
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="4" class="mensagem-erro">${escaparHtml(e.message)}</td></tr>`;
    return;
  }
  tbody.innerHTML = registros.map((g) => `
    <tr class="clicavel" data-id="${g.id}">
      <td>${escaparHtml(g.fornecedor_nome || "—")}</td><td>${escaparHtml(g.protocolo || "—")}</td>
      <td>${escaparHtml(g.situacao)}</td><td>${escaparHtml(g.previsao_retorno || "—")}</td>
    </tr>
  `).join("");
  tbody.querySelectorAll("tr").forEach((linha) => {
    linha.addEventListener("click", () => {
      tbody.querySelectorAll("tr").forEach((l) => l.style.background = "");
      linha.style.background = "#eef2ff";
      const registro = registros.find((r) => r.id === parseInt(linha.dataset.id, 10));
      botaoRetorno.disabled = registro.situacao === "Retornado";
      botaoRetorno.onclick = () => abrirDialogoRetornoGarantia(registro);
    });
  });
}

function abrirDialogoNovaGarantia() {
  const html = `
    <div class="grupo-form"><label>Protocolo</label><input id="dlg-gar-protocolo"></div>
    <div class="grupo-form" style="margin-top:8px;"><label>Motivo</label><input id="dlg-gar-motivo"></div>
    <div class="grupo-form" style="margin-top:8px;"><label>Data de envio</label><input type="date" id="dlg-gar-envio" value="${new Date().toISOString().slice(0, 10)}"></div>
    <div class="grupo-form" style="margin-top:8px;"><label>Previsão de retorno</label><input type="date" id="dlg-gar-previsao"></div>
  `;
  abrirDialogoGenerico("Registrar Envio para Garantia", html, async () => {
    const dados = {
      protocolo: document.getElementById("dlg-gar-protocolo").value.trim() || null,
      motivo: document.getElementById("dlg-gar-motivo").value.trim() || null,
      data_envio: document.getElementById("dlg-gar-envio").value || null,
      previsao_retorno: document.getElementById("dlg-gar-previsao").value || null,
      situacao: "Enviado",
    };
    await ClienteAPI.criarGarantia(_fichaDados.id, dados);
    await carregarTabelaGarantia();
  });
}

function abrirDialogoRetornoGarantia(registro) {
  const html = `
    <p>Origem: ${escaparHtml(registro.fornecedor_nome || "Fornecedor")} (automático)</p>
    <div class="grupo-form"><label>Destino</label><input id="dlg-ret-destino" placeholder="ex: Engenharia Clínica"></div>
    <div class="grupo-form" style="margin-top:8px;"><label>Observação</label><textarea id="dlg-ret-obs" rows="2"></textarea></div>
  `;
  abrirDialogoGenerico(`Retorno da Garantia #${registro.id}`, html, async () => {
    const destino = document.getElementById("dlg-ret-destino").value.trim();
    if (!destino) { alert("Informe o destino."); throw new Error("cancelado"); }
    await ClienteAPI.registrarRetornoGarantia(_fichaDados.id, registro.id, {
      destino, observacao: document.getElementById("dlg-ret-obs").value.trim() || null,
    });
    await carregarTabelaGarantia();
  }, "Confirmar retorno");
}

// ================================================================ ANOTAÇÕES

async function renderizarAbaAnotacoes() {
  const corpo = document.getElementById("ficha-corpo");
  corpo.innerHTML = `
    <textarea id="campo-nova-anotacao" rows="3" style="width:100%;" placeholder="Escreva uma nova anotação…"></textarea>
    <button id="botao-nova-anotacao" style="margin-top:8px;">+ NOVA ANOTAÇÃO</button>
    <div id="lista-anotacoes" style="margin-top:16px;"></div>
  `;
  document.getElementById("botao-nova-anotacao").addEventListener("click", async () => {
    const texto = document.getElementById("campo-nova-anotacao").value.trim();
    if (!texto) { alert("Escreva o texto da anotação."); return; }
    try {
      await ClienteAPI.criarAnotacao(_fichaDados.id, texto);
    } catch (e) {
      alert("Não foi possível salvar: " + e.message);
      return;
    }
    document.getElementById("campo-nova-anotacao").value = "";
    await carregarListaAnotacoes();
  });
  await carregarListaAnotacoes();
}

async function carregarListaAnotacoes() {
  const div = document.getElementById("lista-anotacoes");
  let anotacoes;
  try {
    anotacoes = await ClienteAPI.listarAnotacoes(_fichaDados.id);
  } catch (e) {
    div.innerHTML = `<p class="mensagem-erro">${escaparHtml(e.message)}</p>`;
    return;
  }
  if (anotacoes.length === 0) {
    div.innerHTML = `<p class="mensagem-info">Nenhuma anotação registrada ainda.</p>`;
    return;
  }
  div.innerHTML = anotacoes.map((a) => `
    <div class="timeline-item"><b>${formatarDataHora(a.data_hora)} — ${escaparHtml(a.usuario_nome || "—")}</b><br>${escaparHtml(a.texto)}</div>
  `).join("");
}

// ================================================================ DOCUMENTOS

async function renderizarAbaDocumentos() {
  const corpo = document.getElementById("ficha-corpo");
  const opcoesTipos = TIPOS_DOCUMENTO.map((t) => `<option value="${t}">${t}</option>`).join("");
  corpo.innerHTML = `
    <div class="linha-form">
      <select id="doc-tipo">${opcoesTipos}</select>
      <input type="file" id="doc-arquivo">
      <button id="botao-anexar-doc">📎 Anexar arquivo</button>
    </div>
    <table style="margin-top:12px;">
      <thead><tr><th>Tipo</th><th>Arquivo</th><th>Enviado em</th><th>Enviado por</th></tr></thead>
      <tbody id="tabela-documentos"></tbody>
    </table>
  `;
  document.getElementById("botao-anexar-doc").addEventListener("click", async () => {
    const arquivo = document.getElementById("doc-arquivo").files[0];
    if (!arquivo) { alert("Escolha um arquivo primeiro."); return; }
    try {
      await ClienteAPI.enviarDocumento(_fichaDados.id, document.getElementById("doc-tipo").value, arquivo);
    } catch (e) {
      alert("Não foi possível enviar: " + e.message);
      return;
    }
    document.getElementById("doc-arquivo").value = "";
    await carregarTabelaDocumentos();
  });
  await carregarTabelaDocumentos();
}

async function carregarTabelaDocumentos() {
  const tbody = document.getElementById("tabela-documentos");
  let documentos;
  try {
    documentos = await ClienteAPI.listarDocumentos(_fichaDados.id);
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="4" class="mensagem-erro">${escaparHtml(e.message)}</td></tr>`;
    return;
  }
  tbody.innerHTML = documentos.map((doc) => `
    <tr>
      <td>${escaparHtml(doc.tipo)}</td>
      <td><a href="${ClienteAPI.urlDownloadDocumento(_fichaDados.id, doc.id)}" target="_blank">${escaparHtml(doc.nome_arquivo)}</a></td>
      <td>${formatarDataHora(doc.enviado_em)}</td>
      <td>${escaparHtml(doc.usuario_nome || "—")}</td>
    </tr>
  `).join("");
}

// =========================================================== DIÁLOGO GENÉRICO
// (usado por nova movimentação / manutenção / garantia / retorno)

function abrirDialogoGenerico(titulo, htmlCorpo, aoConfirmar, textoBotao = "Registrar") {
  const fundo = document.createElement("div");
  fundo.className = "modal-fundo";
  fundo.style.zIndex = "200";
  fundo.innerHTML = `
    <div class="modal-caixa" style="height:auto; max-width:480px;">
      <div class="modal-cabecalho"><b>${escaparHtml(titulo)}</b></div>
      <div class="modal-corpo">${htmlCorpo}
        <div style="margin-top:16px;">
          <button id="dlg-generico-ok">${textoBotao}</button>
          <button class="secundario" id="dlg-generico-cancelar">Cancelar</button>
        </div>
        <div class="mensagem-erro oculto" id="dlg-generico-erro"></div>
      </div>
    </div>
  `;
  document.body.appendChild(fundo);
  fundo.querySelector("#dlg-generico-cancelar").addEventListener("click", () => fundo.remove());
  fundo.querySelector("#dlg-generico-ok").addEventListener("click", async () => {
    const erroDiv = fundo.querySelector("#dlg-generico-erro");
    try {
      await aoConfirmar();
      fundo.remove();
    } catch (e) {
      if (e.message === "cancelado") return; // validação interna já mostrou alert
      erroDiv.textContent = e.message || "Erro ao salvar.";
      erroDiv.classList.remove("oculto");
    }
  });
}
