/**
 * Toda comunicação da tela com a API passa por aqui.
 * Como a tela é servida pela própria API (mesma origem), os caminhos são
 * sempre absolutos (ex: "/auth/login") — nunca precisamos configurar
 * endereço de servidor nenhum.
 */

class ErroAPI extends Error {
  constructor(mensagem, statusCode) {
    super(mensagem);
    this.name = "ErroAPI";
    this.statusCode = statusCode;
  }
}

class ErroConexao extends Error {
  constructor(mensagem) {
    super(mensagem);
    this.name = "ErroConexao";
  }
}

const ClienteAPI = {
  obterToken() {
    return sessionStorage.getItem("token");
  },
  definirToken(token) {
    sessionStorage.setItem("token", token);
  },
  limparToken() {
    sessionStorage.removeItem("token");
    sessionStorage.removeItem("usuarioLogado");
  },
  obterUsuarioLogado() {
    const bruto = sessionStorage.getItem("usuarioLogado");
    return bruto ? JSON.parse(bruto) : null;
  },
  definirUsuarioLogado(usuario) {
    sessionStorage.setItem("usuarioLogado", JSON.stringify(usuario));
  },

  async _requisicao(metodo, caminho, { corpoJson, corpoFormData } = {}) {
    const headers = {};
    const token = this.obterToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
    if (corpoJson !== undefined) headers["Content-Type"] = "application/json";

    let resposta;
    try {
      resposta = await fetch(caminho, {
        method: metodo,
        headers,
        body: corpoJson !== undefined ? JSON.stringify(corpoJson) : corpoFormData,
      });
    } catch (erro) {
      throw new ErroConexao("Não foi possível conectar ao servidor. Verifique sua conexão.");
    }

    if (resposta.status === 401 && token) {
      // Só trata como "sessão expirou" quando a requisição JÁ tinha um token
      // (ou seja, não é a tentativa de login em si — essa tem seu próprio
      // tratamento de erro na tela de login).
      this.limparToken();
      window.dispatchEvent(new CustomEvent("sessao-expirada"));
    }

    if (!resposta.ok) {
      let detalhe = resposta.statusText || "Erro desconhecido";
      try {
        const dados = await resposta.json();
        if (dados && dados.detail) detalhe = dados.detail;
      } catch (_) {
        /* resposta sem corpo JSON — mantém a mensagem padrão */
      }
      throw new ErroAPI(detalhe, resposta.status);
    }

    if (resposta.status === 204) return null;
    const tipoConteudo = resposta.headers.get("content-type") || "";
    if (tipoConteudo.includes("application/json")) return resposta.json();
    return resposta; // chamador trata (ex: download de arquivo)
  },

  get(caminho, params) {
    let url = caminho;
    if (params) {
      const entradas = Object.entries(params).filter(
        ([, v]) => v !== undefined && v !== null && v !== ""
      );
      if (entradas.length) url += `?${new URLSearchParams(entradas).toString()}`;
    }
    return this._requisicao("GET", url);
  },
  post(caminho, corpoJson) {
    return this._requisicao("POST", caminho, { corpoJson });
  },
  put(caminho, corpoJson) {
    return this._requisicao("PUT", caminho, { corpoJson });
  },
  postFormData(caminho, formData) {
    return this._requisicao("POST", caminho, { corpoFormData: formData });
  },

  // ---- Autenticação ----
  async login(usuario, senha) {
    const dados = await this.post("/auth/login", { usuario, senha });
    this.definirToken(dados.access_token);
    const usuarioLogado = await this.get("/usuarios/me");
    this.definirUsuarioLogado(usuarioLogado);
    return usuarioLogado;
  },
  logout() {
    this.limparToken();
  },

  // ---- Patrimônios ----
  buscarPatrimonios(busca) {
    return this.get("/patrimonios", busca ? { busca } : undefined);
  },
  obterPatrimonio(id) {
    return this.get(`/patrimonios/${id}`);
  },
  criarPatrimonio(dados) {
    return this.post("/patrimonios", dados);
  },
  atualizarPatrimonio(id, dados) {
    return this.put(`/patrimonios/${id}`, dados);
  },

  // ---- Cadastros auxiliares ----
  listarItens() { return this.get("/itens"); },
  criarItem(dados) { return this.post("/itens", dados); },
  listarCategorias() { return this.get("/categorias"); },
  criarCategoria(dados) { return this.post("/categorias", dados); },
  listarMarcas() { return this.get("/marcas"); },
  criarMarca(dados) { return this.post("/marcas", dados); },
  listarModelos(marcaId) { return this.get("/modelos", marcaId ? { marca_id: marcaId } : undefined); },
  criarModelo(dados) { return this.post("/modelos", dados); },
  listarSecretarias() { return this.get("/secretarias"); },
  criarSecretaria(dados) { return this.post("/secretarias", dados); },
  listarSetores(secretariaId) { return this.get("/setores", secretariaId ? { secretaria_id: secretariaId } : undefined); },
  criarSetor(dados) { return this.post("/setores", dados); },
  listarLocais(setorId) { return this.get("/locais", setorId ? { setor_id: setorId } : undefined); },
  criarLocal(dados) { return this.post("/locais", dados); },
  listarFornecedores(busca) { return this.get("/fornecedores", busca ? { busca } : undefined); },
  criarFornecedor(dados) { return this.post("/fornecedores", dados); },
  listarEmpenhos() { return this.get("/empenhos"); },
  criarEmpenho(dados) { return this.post("/empenhos", dados); },
  listarAquisicoes() { return this.get("/aquisicoes"); },
  criarAquisicao(dados) { return this.post("/aquisicoes", dados); },

  // ---- Movimentações / Histórico ----
  listarMovimentacoes(patrimonioId) { return this.get(`/patrimonios/${patrimonioId}/movimentacoes`); },
  criarMovimentacao(patrimonioId, dados) { return this.post(`/patrimonios/${patrimonioId}/movimentacoes`, dados); },

  // ---- Manutenção ----
  listarManutencoes(patrimonioId) { return this.get(`/patrimonios/${patrimonioId}/manutencoes`); },
  criarManutencao(patrimonioId, dados) { return this.post(`/patrimonios/${patrimonioId}/manutencoes`, dados); },
  atualizarManutencao(patrimonioId, manutencaoId, dados) {
    return this.put(`/patrimonios/${patrimonioId}/manutencoes/${manutencaoId}`, dados);
  },

  // ---- Garantia ----
  listarGarantias(patrimonioId) { return this.get(`/patrimonios/${patrimonioId}/garantias`); },
  criarGarantia(patrimonioId, dados) { return this.post(`/patrimonios/${patrimonioId}/garantias`, dados); },
  registrarRetornoGarantia(patrimonioId, garantiaId, dados) {
    return this.post(`/patrimonios/${patrimonioId}/garantias/${garantiaId}/retorno`, dados);
  },

  // ---- Anotações ----
  listarAnotacoes(patrimonioId) { return this.get(`/patrimonios/${patrimonioId}/anotacoes`); },
  criarAnotacao(patrimonioId, texto) { return this.post(`/patrimonios/${patrimonioId}/anotacoes`, { texto }); },

  // ---- Documentos ----
  listarDocumentos(patrimonioId) { return this.get(`/patrimonios/${patrimonioId}/documentos`); },
  async enviarDocumento(patrimonioId, tipo, arquivo) {
    const formData = new FormData();
    formData.append("tipo", tipo);
    formData.append("arquivo", arquivo);
    return this.postFormData(`/patrimonios/${patrimonioId}/documentos`, formData);
  },
  urlDownloadDocumento(patrimonioId, documentoId) {
    return `/patrimonios/${patrimonioId}/documentos/${documentoId}/download`;
  },

  // ---- Relatórios ----
  relatorio(nome, params) { return this.get(`/relatorios/${nome}`, params); },

  // ---- Dashboard / Pendências / Auditoria ----
  resumoDashboard() { return this.get("/dashboard/resumo"); },
  resumoPendencias() { return this.get("/pendencias/resumo"); },
  listarAuditoria(patrimonioId) { return this.get("/auditoria", patrimonioId ? { patrimonio_id: patrimonioId } : undefined); },

  // ---- Usuários ----
  listarUsuarios() { return this.get("/usuarios"); },
  criarUsuario(dados) { return this.post("/usuarios", dados); },
  atualizarUsuario(id, dados) { return this.put(`/usuarios/${id}`, dados); },
  listarPerfis() { return this.get("/perfis"); },
};

// Permite testar este arquivo com Node (bateria de testes), sem afetar o navegador
// (no navegador, "module" não existe, então este bloco simplesmente não roda).
if (typeof module !== "undefined" && module.exports) {
  module.exports = { ClienteAPI, ErroAPI, ErroConexao };
}
