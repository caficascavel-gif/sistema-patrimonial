// Cada entrada descreve uma tela de cadastro simples: como listar, como
// criar, e quais campos o formulário tem (texto simples ou select vindo de
// outro cadastro).
const DEFINICOES_CADASTRO = {
  categorias: {
    titulo: "Categorias", campos: [{ chave: "nome", rotulo: "Nome", tipo: "texto" }],
    listar: () => ClienteAPI.listarCategorias(), criar: (d) => ClienteAPI.criarCategoria(d),
  },
  marcas: {
    titulo: "Marcas", campos: [{ chave: "nome", rotulo: "Nome", tipo: "texto" }],
    listar: () => ClienteAPI.listarMarcas(), criar: (d) => ClienteAPI.criarMarca(d),
  },
  modelos: {
    titulo: "Modelos",
    campos: [
      { chave: "marca_id", rotulo: "Marca", tipo: "select", opcoes: () => ClienteAPI.listarMarcas() },
      { chave: "nome", rotulo: "Nome", tipo: "texto" },
    ],
    listar: () => ClienteAPI.listarModelos(), criar: (d) => ClienteAPI.criarModelo(d),
  },
  secretarias: {
    titulo: "Secretarias", campos: [{ chave: "nome", rotulo: "Nome", tipo: "texto" }],
    listar: () => ClienteAPI.listarSecretarias(), criar: (d) => ClienteAPI.criarSecretaria(d),
  },
  setores: {
    titulo: "Setores",
    campos: [
      { chave: "secretaria_id", rotulo: "Secretaria", tipo: "select", opcoes: () => ClienteAPI.listarSecretarias() },
      { chave: "nome", rotulo: "Nome", tipo: "texto" },
    ],
    listar: () => ClienteAPI.listarSetores(), criar: (d) => ClienteAPI.criarSetor(d),
  },
  locais: {
    titulo: "Locais",
    campos: [
      { chave: "setor_id", rotulo: "Setor", tipo: "select", opcoes: () => ClienteAPI.listarSetores() },
      { chave: "nome", rotulo: "Nome", tipo: "texto" },
    ],
    listar: () => ClienteAPI.listarLocais(), criar: (d) => ClienteAPI.criarLocal(d),
  },
  fornecedores: {
    titulo: "Fornecedores",
    campos: [
      { chave: "razao_social", rotulo: "Razão social", tipo: "texto" },
      { chave: "cnpj", rotulo: "CNPJ", tipo: "texto" },
      { chave: "telefone", rotulo: "Telefone", tipo: "texto" },
      { chave: "email", rotulo: "E-mail", tipo: "texto" },
    ],
    listar: () => ClienteAPI.listarFornecedores(), criar: (d) => ClienteAPI.criarFornecedor(d),
  },
  itens: {
    titulo: "Itens/Equipamentos",
    campos: [
      { chave: "descricao", rotulo: "Descrição", tipo: "texto" },
      { chave: "categoria_id", rotulo: "Categoria", tipo: "select", opcoes: () => ClienteAPI.listarCategorias() },
      { chave: "marca_id", rotulo: "Marca", tipo: "select", opcoes: () => ClienteAPI.listarMarcas() },
    ],
    listar: () => ClienteAPI.listarItens(), criar: (d) => ClienteAPI.criarItem(d),
  },
  empenhos: {
    titulo: "Empenhos/NE",
    campos: [
      { chave: "numero", rotulo: "Número", tipo: "texto" },
      { chave: "ano", rotulo: "Ano", tipo: "numero" },
      { chave: "fornecedor_id", rotulo: "Fornecedor", tipo: "select", opcoes: () => ClienteAPI.listarFornecedores() },
    ],
    listar: () => ClienteAPI.listarEmpenhos(), criar: (d) => ClienteAPI.criarEmpenho(d),
  },
  aquisicoes: {
    titulo: "Aquisições",
    campos: [
      { chave: "fornecedor_id", rotulo: "Fornecedor", tipo: "select", opcoes: () => ClienteAPI.listarFornecedores() },
      { chave: "empenho_id", rotulo: "Empenho", tipo: "select", opcoes: () => ClienteAPI.listarEmpenhos() },
      { chave: "nota_fiscal", rotulo: "Nota fiscal", tipo: "texto" },
    ],
    listar: () => ClienteAPI.listarAquisicoes(), criar: (d) => ClienteAPI.criarAquisicao(d),
  },
};

let _cadastroAtivo = null;

function inicializarCadastros() {
  const container = document.getElementById("lista-botoes-cadastro");
  Object.entries(DEFINICOES_CADASTRO).forEach(([chave, def]) => {
    const botao = document.createElement("button");
    botao.className = "secundario";
    botao.textContent = def.titulo;
    botao.addEventListener("click", () => abrirCadastro(chave));
    container.appendChild(botao);
  });
}

async function abrirCadastro(chave) {
  _cadastroAtivo = chave;
  const def = DEFINICOES_CADASTRO[chave];
  document.getElementById("cartao-cadastro-ativo").classList.remove("oculto");
  document.getElementById("titulo-cadastro-ativo").textContent = def.titulo;

  // monta o formulário (carregando opções de selects em paralelo)
  const opcoesPorCampo = {};
  await Promise.all(
    def.campos.filter((c) => c.tipo === "select").map(async (c) => { opcoesPorCampo[c.chave] = await c.opcoes(); })
  );

  const formulario = document.getElementById("formulario-cadastro-ativo");
  formulario.innerHTML = `<div class="linha-form">` +
    def.campos.map((c) => {
      if (c.tipo === "select") {
        const opcoes = opcoesPorCampo[c.chave].map((o) => `<option value="${o.id}">${escaparHtml(o.nome)}</option>`).join("");
        return `<div class="grupo-form"><label>${c.rotulo}</label><select id="novo-${c.chave}">${opcoes}</select></div>`;
      }
      const tipoInput = c.tipo === "numero" ? "number" : "text";
      return `<div class="grupo-form"><label>${c.rotulo}</label><input type="${tipoInput}" id="novo-${c.chave}"></div>`;
    }).join("") +
    `<button id="botao-salvar-novo-cadastro" style="align-self:flex-end;">Adicionar</button></div>
     <div class="mensagem-erro oculto" id="erro-novo-cadastro"></div>`;

  document.getElementById("botao-salvar-novo-cadastro").addEventListener("click", async () => {
    const dados = {};
    def.campos.forEach((c) => {
      const valorBruto = document.getElementById(`novo-${c.chave}`).value;
      dados[c.chave] = c.tipo === "numero" || c.tipo === "select" ? (valorBruto ? parseInt(valorBruto, 10) : null) : valorBruto.trim();
    });
    const erroDiv = document.getElementById("erro-novo-cadastro");
    erroDiv.classList.add("oculto");
    try {
      await def.criar(dados);
    } catch (e) {
      erroDiv.textContent = e.message;
      erroDiv.classList.remove("oculto");
      return;
    }
    await carregarTabelaCadastro(chave);
  });

  await carregarTabelaCadastro(chave);
}

async function carregarTabelaCadastro(chave) {
  const def = DEFINICOES_CADASTRO[chave];
  const cabecalho = document.getElementById("cabecalho-cadastro-ativo");
  const corpo = document.getElementById("corpo-cadastro-ativo");

  const nomesColunas = def.campos.map((c) => c.rotulo);
  cabecalho.innerHTML = `<tr>${nomesColunas.map((n) => `<th>${n}</th>`).join("")}</tr>`;

  let itens;
  try {
    itens = await def.listar();
  } catch (e) {
    corpo.innerHTML = `<tr><td colspan="${nomesColunas.length}" class="mensagem-erro">${escaparHtml(e.message)}</td></tr>`;
    return;
  }

  // resolve nomes de FKs pra exibição (busca as listas auxiliares só quando precisa)
  const auxiliares = {};
  for (const c of def.campos) {
    if (c.tipo === "select") {
      const chaveAux = c.chave.replace("_id", "") + "s"; // ex: marca_id -> marcas
      if (!auxiliares[chaveAux]) auxiliares[chaveAux] = await c.opcoes();
    }
  }

  corpo.innerHTML = itens.map((item) => `
    <tr>${def.campos.map((c) => {
      if (c.tipo === "select") {
        const chaveAux = c.chave.replace("_id", "") + "s";
        const encontrado = (auxiliares[chaveAux] || []).find((o) => o.id === item[c.chave]);
        return `<td>${escaparHtml(encontrado ? encontrado.nome : "—")}</td>`;
      }
      return `<td>${escaparHtml(item[c.chave] ?? "—")}</td>`;
    }).join("")}</tr>
  `).join("");
}
