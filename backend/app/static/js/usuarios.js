let _perfisCache = null;

function inicializarUsuarios() {
  document.getElementById("botao-novo-usuario").addEventListener("click", abrirDialogoNovoUsuario);
}

async function carregarUsuarios() {
  const tbody = document.getElementById("tabela-usuarios");
  tbody.innerHTML = `<tr><td colspan="5" class="mensagem-info">Carregando…</td></tr>`;
  let usuarios, perfis;
  try {
    [usuarios, perfis] = await Promise.all([ClienteAPI.listarUsuarios(), obterPerfisCache()]);
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="5" class="mensagem-erro">${escaparHtml(e.message)}</td></tr>`;
    return;
  }
  tbody.innerHTML = usuarios.map((u) => {
    const perfil = perfis.find((p) => p.id === u.perfil_id);
    return `
    <tr>
      <td>${escaparHtml(u.nome)}</td><td>${escaparHtml(u.usuario)}</td>
      <td>${escaparHtml(perfil ? perfil.nome : "—")}</td><td>${u.ativo ? "Sim" : "Não"}</td>
      <td><button class="secundario botao-editar-usuario" data-id="${u.id}">Editar</button></td>
    </tr>
  `;
  }).join("");
  tbody.querySelectorAll(".botao-editar-usuario").forEach((botao) => {
    botao.addEventListener("click", () => {
      const usuario = usuarios.find((u) => u.id === parseInt(botao.dataset.id, 10));
      abrirDialogoEditarUsuario(usuario);
    });
  });
}

async function obterPerfisCache() {
  if (!_perfisCache) _perfisCache = await ClienteAPI.listarPerfis();
  return _perfisCache;
}

async function abrirDialogoNovoUsuario() {
  const perfis = await obterPerfisCache();
  const opcoes = perfis.map((p) => `<option value="${p.id}">${escaparHtml(p.nome)}</option>`).join("");
  const html = `
    <div class="grupo-form"><label>Nome completo</label><input id="dlg-usr-nome"></div>
    <div class="grupo-form" style="margin-top:8px;"><label>Usuário (login)</label><input id="dlg-usr-login"></div>
    <div class="grupo-form" style="margin-top:8px;"><label>Senha</label><input type="password" id="dlg-usr-senha"></div>
    <div class="grupo-form" style="margin-top:8px;"><label>Perfil</label><select id="dlg-usr-perfil">${opcoes}</select></div>
  `;
  abrirDialogoGenerico("Novo usuário", html, async () => {
    const dados = {
      nome: document.getElementById("dlg-usr-nome").value.trim(),
      usuario: document.getElementById("dlg-usr-login").value.trim(),
      senha: document.getElementById("dlg-usr-senha").value,
      perfil_id: parseInt(document.getElementById("dlg-usr-perfil").value, 10),
    };
    if (!dados.nome || !dados.usuario || !dados.senha) {
      alert("Preencha nome, usuário e senha.");
      throw new Error("cancelado");
    }
    await ClienteAPI.criarUsuario(dados);
    await carregarUsuarios();
  }, "Criar");
}

async function abrirDialogoEditarUsuario(usuario) {
  const perfis = await obterPerfisCache();
  const opcoes = perfis.map((p) => `<option value="${p.id}" ${p.id === usuario.perfil_id ? "selected" : ""}>${escaparHtml(p.nome)}</option>`).join("");
  const html = `
    <div class="grupo-form"><label>Nome completo</label><input id="dlg-usr2-nome" value="${escaparHtml(usuario.nome)}"></div>
    <div class="grupo-form" style="margin-top:8px;"><label>Perfil</label><select id="dlg-usr2-perfil">${opcoes}</select></div>
    <div class="grupo-form" style="margin-top:8px;"><label>Nova senha (deixe em branco para não trocar)</label><input type="password" id="dlg-usr2-senha"></div>
    <div class="grupo-form" style="margin-top:8px;"><label><input type="checkbox" id="dlg-usr2-ativo" ${usuario.ativo ? "checked" : ""}> Ativo</label></div>
  `;
  abrirDialogoGenerico(`Editar usuário — ${usuario.usuario}`, html, async () => {
    const dados = {
      nome: document.getElementById("dlg-usr2-nome").value.trim(),
      perfil_id: parseInt(document.getElementById("dlg-usr2-perfil").value, 10),
      ativo: document.getElementById("dlg-usr2-ativo").checked,
    };
    const novaSenha = document.getElementById("dlg-usr2-senha").value;
    if (novaSenha) dados.senha = novaSenha;
    await ClienteAPI.atualizarUsuario(usuario.id, dados);
    await carregarUsuarios();
  }, "Salvar");
}
