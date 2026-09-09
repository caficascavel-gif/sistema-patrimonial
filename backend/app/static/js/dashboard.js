const CARTOES_DASHBOARD = [
  ["total", "PATRIMÔNIOS"], ["em_uso", "EM USO"], ["em_manutencao", "MANUTENÇÃO"],
  ["em_garantia", "GARANTIA"], ["sem_local", "SEM LOCAL"], ["baixados", "BAIXADOS"],
];

const PENDENCIAS_ROTULOS = [
  ["patrimonios_sem_fornecedor", "patrimônio(s) sem fornecedor"],
  ["patrimonios_sem_ne", "patrimônio(s) sem NE"],
  ["patrimonios_sem_localizacao", "patrimônio(s) sem localização"],
  ["patrimonios_sem_numero_serie", "patrimônio(s) sem número de série"],
  ["aquisicoes_sem_patrimonio", "aquisição(ões) sem patrimônio vinculado"],
];

async function carregarDashboard() {
  const grade = document.getElementById("grade-indicadores");
  const listaPendencias = document.getElementById("lista-pendencias");
  grade.innerHTML = `<p class="mensagem-info">Carregando…</p>`;
  listaPendencias.innerHTML = "";

  let dadosDashboard, dadosPendencias;
  try {
    [dadosDashboard, dadosPendencias] = await Promise.all([
      ClienteAPI.resumoDashboard(), ClienteAPI.resumoPendencias(),
    ]);
  } catch (e) {
    grade.innerHTML = `<p class="mensagem-erro">${escaparHtml(e.message)}</p>`;
    return;
  }

  grade.innerHTML = CARTOES_DASHBOARD.map(([chave, rotulo]) => `
    <div class="cartao-indicador"><div class="valor">${dadosDashboard[chave] ?? 0}</div><div class="rotulo">${rotulo}</div></div>
  `).join("");

  const pendenciasComValor = PENDENCIAS_ROTULOS.filter(([chave]) => (dadosPendencias[chave] || 0) > 0);
  if (pendenciasComValor.length === 0) {
    listaPendencias.innerHTML = `<p class="mensagem-info">🟢 Nenhuma pendência encontrada.</p>`;
    return;
  }
  listaPendencias.innerHTML = pendenciasComValor.map(([chave, texto]) => `
    <div><button class="secundario botao-pendencia" style="text-align:left; width:100%; margin-bottom:6px;">⚠ ${dadosPendencias[chave]} ${texto}</button></div>
  `).join("");
  listaPendencias.querySelectorAll(".botao-pendencia").forEach((botao) => {
    botao.addEventListener("click", async () => {
      mostrarTela("relatorios");
      const def = RELATORIOS_DISPONIVEIS.find((r) => r.nome === "incompletos");
      await abrirRelatorio(def);
    });
  });
}
