let _resultadosAtuais = [];

function inicializarPrincipal() {
  document.getElementById("botao-pesquisar").addEventListener("click", pesquisarPatrimonios);
  document.getElementById("campo-busca").addEventListener("keydown", (e) => {
    if (e.key === "Enter") pesquisarPatrimonios();
  });
  document.getElementById("botao-novo-patrimonio").addEventListener("click", abrirNovoPatrimonio);
}

async function pesquisarPatrimonios() {
  const termo = document.getElementById("campo-busca").value.trim();
  const corpoTabela = document.getElementById("tabela-patrimonios");
  const contador = document.getElementById("contador-resultados");

  try {
    _resultadosAtuais = await ClienteAPI.buscarPatrimonios(termo);
  } catch (e) {
    contador.textContent = `Erro: ${e.message}`;
    return;
  }

  corpoTabela.innerHTML = "";
  _resultadosAtuais.forEach((p, indice) => {
    const linha = document.createElement("tr");
    linha.className = "clicavel";
    linha.innerHTML = `
      <td>${escaparHtml(p.numero_patrimonio)}</td>
      <td>${escaparHtml(p.item_descricao || "—")}</td>
      <td>${escaparHtml(p.local_descricao || "—")}</td>
      <td>${iconeSituacao(p.situacao_atual)} ${escaparHtml(p.situacao_atual)}</td>
      <td>${pillCadastro(p.status_cadastro)}</td>
    `;
    linha.addEventListener("click", () => abrirFicha(_resultadosAtuais, indice));
    corpoTabela.appendChild(linha);
  });

  contador.textContent = `${_resultadosAtuais.length} patrimônio(s) encontrado(s).`;
}

async function abrirNovoPatrimonio() {
  let itens;
  try {
    itens = await ClienteAPI.listarItens();
  } catch (e) {
    alert("Erro ao carregar equipamentos: " + e.message);
    return;
  }
  if (itens.length === 0) {
    alert("Cadastre um Item/Equipamento antes (tela Cadastros) para poder criar um patrimônio.");
    return;
  }

  const numero = prompt("Número do patrimônio:");
  if (!numero) return;
  const opcoesItens = itens.map((i) => `${i.id} = ${i.descricao}`).join("\n");
  const itemIdTexto = prompt(`ID do equipamento:\n${opcoesItens}`);
  const itemId = parseInt(itemIdTexto, 10);
  if (!itemId) return;

  try {
    const novo = await ClienteAPI.criarPatrimonio({ numero_patrimonio: numero, item_id: itemId });
    document.getElementById("campo-busca").value = ""; // senão um filtro antigo pode escondê-lo da lista
    await pesquisarPatrimonios();
    const indice = _resultadosAtuais.findIndex((p) => p.id === novo.id);
    if (indice >= 0) {
      abrirFicha(_resultadosAtuais, indice);
    } else {
      alert("Patrimônio criado, mas não foi possível localizá-lo na lista para abrir a ficha automaticamente.");
    }
  } catch (e) {
    alert("Não foi possível criar: " + e.message);
  }
}
