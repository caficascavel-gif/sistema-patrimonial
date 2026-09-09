const RELATORIOS_DISPONIVEIS = [
  { titulo: "Patrimônio geral", nome: "patrimonio-geral", colunas: [["numero_patrimonio","Patrimônio"],["equipamento","Equipamento"],["setor","Setor"],["local","Local"],["situacao","Situação"],["fornecedor","Fornecedor"],["ne","NE"]] },
  { titulo: "Equipamentos em manutenção", nome: "em-manutencao", colunas: [["numero_patrimonio","Patrimônio"],["equipamento","Equipamento"],["data","Data"],["situacao","Situação"],["problema_relatado","Problema"],["responsavel","Responsável"]] },
  { titulo: "Equipamentos em garantia", nome: "em-garantia", colunas: [["numero_patrimonio","Patrimônio"],["equipamento","Equipamento"],["fornecedor","Fornecedor"],["situacao","Situação"],["data_envio","Envio"],["previsao_retorno","Previsão"]] },
  { titulo: "Equipamentos por setor", nome: "por-setor", colunas: [["numero_patrimonio","Patrimônio"],["equipamento","Equipamento"],["setor","Setor"],["local","Local"],["situacao","Situação"]] },
  { titulo: "Equipamentos por fornecedor", nome: "por-fornecedor", colunas: [["numero_patrimonio","Patrimônio"],["equipamento","Equipamento"],["fornecedor","Fornecedor"],["ne","NE"]] },
  { titulo: "Equipamentos por empenho", nome: "por-empenho", colunas: [["numero_patrimonio","Patrimônio"],["equipamento","Equipamento"],["fornecedor","Fornecedor"],["ne","NE"]] },
  { titulo: "Patrimônios sem informações completas", nome: "incompletos", colunas: [["numero_patrimonio","Patrimônio"],["equipamento","Equipamento"],["setor","Setor"],["situacao","Situação"],["pendencias","Pendências"]] },
];

let _relatorioAtual = null;

function inicializarRelatorios() {
  const container = document.getElementById("lista-botoes-relatorio");
  RELATORIOS_DISPONIVEIS.forEach((r) => {
    const botao = document.createElement("button");
    botao.className = "secundario";
    botao.textContent = r.titulo;
    botao.addEventListener("click", () => abrirRelatorio(r));
    container.appendChild(botao);
  });

  document.getElementById("botao-imprimir-relatorio").addEventListener("click", () => window.print());
  document.getElementById("botao-exportar-csv").addEventListener("click", exportarRelatorioCsv);
}

async function abrirRelatorio(definicao) {
  let linhas;
  try {
    linhas = await ClienteAPI.relatorio(definicao.nome);
  } catch (e) {
    alert("Erro ao gerar relatório: " + e.message);
    return;
  }
  _relatorioAtual = { definicao, linhas };

  document.getElementById("cartao-resultado-relatorio").classList.remove("oculto");
  document.getElementById("titulo-relatorio").textContent = `${definicao.titulo} (${linhas.length})`;
  document.getElementById("cabecalho-relatorio").innerHTML =
    `<tr>${definicao.colunas.map(([, rotulo]) => `<th>${rotulo}</th>`).join("")}</tr>`;
  document.getElementById("corpo-relatorio").innerHTML = linhas.map((linha) => `
    <tr>${definicao.colunas.map(([chave]) => `<td>${escaparHtml(linha[chave] ?? "—")}</td>`).join("")}</tr>
  `).join("");
}

function exportarRelatorioCsv() {
  if (!_relatorioAtual) return;
  const { definicao, linhas } = _relatorioAtual;
  const cabecalho = definicao.colunas.map(([, rotulo]) => `"${rotulo}"`).join(";");
  const corpo = linhas.map((linha) =>
    definicao.colunas.map(([chave]) => `"${String(linha[chave] ?? "").replace(/"/g, '""')}"`).join(";")
  ).join("\n");
  const csv = "\uFEFF" + cabecalho + "\n" + corpo; // BOM pro Excel abrir acentuação certa

  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `${definicao.titulo}.csv`;
  link.click();
  URL.revokeObjectURL(link.href);
}
