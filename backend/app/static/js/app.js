const CARREGADORES_TELA = {
  principal: () => pesquisarPatrimonios(),
  dashboard: () => carregarDashboard(),
  relatorios: () => {}, // a lista de botões já foi montada na inicialização
  cadastros: () => {},
  auditoria: () => carregarAuditoria(),
  usuarios: () => carregarUsuarios(),
};

function mostrarTela(nome) {
  document.querySelectorAll(".tela").forEach((secao) => secao.classList.add("oculto"));
  document.getElementById(`tela-${nome}`).classList.remove("oculto");
  const carregador = CARREGADORES_TELA[nome];
  if (carregador) carregador();
}

function inicializarNavegacao() {
  document.querySelectorAll("#cabecalho nav button").forEach((botao) => {
    botao.addEventListener("click", () => mostrarTela(botao.dataset.tela));
  });
}

document.addEventListener("DOMContentLoaded", () => {
  inicializarLogin();
  inicializarSair();
  inicializarNavegacao();
  inicializarPrincipal();
  inicializarFicha();
  inicializarCadastros();
  inicializarRelatorios();
  inicializarUsuarios();

  window.addEventListener("sessao-expirada", () => {
    document.getElementById("app").classList.add("oculto");
    document.getElementById("tela-login").classList.remove("oculto");
    const erro = document.getElementById("login-erro");
    erro.textContent = "Sua sessão expirou. Faça login novamente.";
    erro.classList.remove("oculto");
  });

  // se já existe um token válido na sessão (ex: F5 na página), pula direto pro app
  const usuarioLogado = ClienteAPI.obterUsuarioLogado();
  if (ClienteAPI.obterToken() && usuarioLogado) {
    aoLogar(usuarioLogado);
  }
});
