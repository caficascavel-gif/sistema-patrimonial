const ICONE_SITUACAO = {
  "Em uso": "🟢", "Disponível": "🟢", "Em manutenção": "🟠",
  "Em garantia": "🟠", "Emprestado": "🔵", "Baixado": "⚪", "Descartado": "⚪",
};

const SITUACOES_PATRIMONIO = [
  "Em uso", "Disponível", "Em manutenção", "Em garantia",
  "Emprestado", "Baixado", "Descartado",
];

const TIPOS_MOVIMENTACAO = [
  "Entrada", "Transferência", "Empréstimo", "Engenharia Clínica",
  "Manutenção", "Garantia", "Retorno de garantia", "Retorno de manutenção",
  "Baixa", "Descarte", "Outros",
];

const SITUACOES_MANUTENCAO = [
  "Em análise", "Em manutenção", "Aguardando peça", "Aguardando fornecedor",
  "Resolvido", "Sem conserto", "Encaminhado para garantia",
];

const SITUACOES_GARANTIA = [
  "Aguardando envio", "Enviado", "Aguardando fornecedor",
  "Em análise", "Concluído", "Retornado", "Sem solução",
];

const TIPOS_DOCUMENTO = [
  "Nota Fiscal", "Empenho", "Termo de garantia", "Ordem de serviço",
  "Laudo técnico", "Comunicação do fornecedor", "Outros",
];

function iconeSituacao(situacao) {
  return ICONE_SITUACAO[situacao] || "";
}

function formatarDataHora(isoString) {
  if (!isoString) return "—";
  return isoString.replace("T", " ").slice(0, 16);
}

function escaparHtml(texto) {
  const div = document.createElement("div");
  div.textContent = texto ?? "";
  return div.innerHTML;
}

function pillCadastro(statusCadastro) {
  if (statusCadastro === "completo") {
    return `<span class="pill pill-completo">🟢 completo</span>`;
  }
  return `<span class="pill pill-incompleto">🟡 incompleto</span>`;
}

function preencherSelect(select, itens, { valor = "id", rotulo = "nome", vazio = null } = {}) {
  select.innerHTML = "";
  if (vazio !== null) {
    const opcaoVazia = document.createElement("option");
    opcaoVazia.value = "";
    opcaoVazia.textContent = vazio;
    select.appendChild(opcaoVazia);
  }
  for (const item of itens) {
    const opcao = document.createElement("option");
    opcao.value = item[valor];
    opcao.textContent = item[rotulo];
    select.appendChild(opcao);
  }
}

// Testável via Node
if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    ICONE_SITUACAO, SITUACOES_PATRIMONIO, TIPOS_MOVIMENTACAO,
    SITUACOES_MANUTENCAO, SITUACOES_GARANTIA, TIPOS_DOCUMENTO,
    iconeSituacao, formatarDataHora, pillCadastro,
  };
}
