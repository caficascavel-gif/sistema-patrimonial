async function carregarAuditoria() {
  const tbody = document.getElementById("tabela-auditoria");
  tbody.innerHTML = `<tr><td colspan="6" class="mensagem-info">Carregando…</td></tr>`;

  let registros;
  try {
    registros = await ClienteAPI.listarAuditoria();
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="6" class="mensagem-erro">${escaparHtml(e.message)}</td></tr>`;
    return;
  }

  if (registros.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="mensagem-info">Nenhum registro de auditoria ainda.</td></tr>`;
    return;
  }

  tbody.innerHTML = registros.map((a) => `
    <tr>
      <td>${formatarDataHora(a.data_hora)}</td>
      <td>${escaparHtml(a.usuario_nome || "—")}</td>
      <td>${escaparHtml(a.numero_patrimonio || "—")}</td>
      <td>${escaparHtml(a.campo || "—")}</td>
      <td>${escaparHtml(a.valor_anterior || "—")}</td>
      <td>${escaparHtml(a.valor_novo || "—")}</td>
    </tr>
  `).join("");
}
