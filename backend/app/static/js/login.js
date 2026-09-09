function inicializarLogin() {
  const form = document.getElementById("form-login");
  const erro = document.getElementById("login-erro");

  form.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    erro.classList.add("oculto");
    const usuario = document.getElementById("login-usuario").value.trim();
    const senha = document.getElementById("login-senha").value;

    try {
      const usuarioLogado = await ClienteAPI.login(usuario, senha);
      aoLogar(usuarioLogado);
    } catch (e) {
      erro.textContent = e.message || "Não foi possível entrar.";
      erro.classList.remove("oculto");
    }
  });
}

function aoLogar(usuarioLogado) {
  document.getElementById("tela-login").classList.add("oculto");
  document.getElementById("app").classList.remove("oculto");
  document.getElementById("info-usuario-logado").textContent =
    `${usuarioLogado.nome} (${usuarioLogado.perfil_nome})`;

  const ehAdministrador = usuarioLogado.perfil_nome === "Administrador";
  document.getElementById("botao-auditoria").classList.toggle("oculto", !ehAdministrador);
  document.getElementById("botao-usuarios").classList.toggle("oculto", !ehAdministrador);

  mostrarTela("principal");
}

function inicializarSair() {
  document.getElementById("botao-sair").addEventListener("click", () => {
    ClienteAPI.logout();
    document.getElementById("app").classList.add("oculto");
    document.getElementById("tela-login").classList.remove("oculto");
    document.getElementById("form-login").reset();
  });
}
