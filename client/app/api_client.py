"""
Toda comunicação do cliente com o sistema passa por aqui.
O cliente NUNCA acessa o MySQL diretamente — só fala com a API via HTTP/REST,
conforme a arquitetura definida na especificação.
"""
import requests

from app.config import obter_url_api


class ErroAPI(Exception):
    """Erro de negócio retornado pela API (ex: 400, 403, 404) com mensagem amigável."""

    def __init__(self, mensagem: str, status_code: int | None = None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.status_code = status_code


class ErroConexao(Exception):
    """Não conseguiu nem falar com o servidor (rede fora do ar, endereço errado etc.)."""


class ClienteAPI:
    def __init__(self):
        self.token: str | None = None
        self.usuario_logado: dict | None = None

    @property
    def base_url(self) -> str:
        url = obter_url_api()
        if not url:
            raise ErroConexao("Endereço do servidor não configurado.")
        return url

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _tratar_resposta(self, resposta: requests.Response):
        if resposta.status_code >= 400:
            try:
                detalhe = resposta.json().get("detail", resposta.text)
            except ValueError:
                detalhe = resposta.text
            raise ErroAPI(str(detalhe), resposta.status_code)
        if resposta.status_code == 204 or not resposta.content:
            return None
        return resposta.json()

    def _request(self, metodo: str, caminho: str, **kwargs):
        try:
            resposta = requests.request(
                metodo, f"{self.base_url}{caminho}", headers=self._headers(), timeout=10, **kwargs
            )
        except requests.exceptions.RequestException as erro:
            raise ErroConexao(f"Não foi possível conectar ao servidor: {erro}") from erro
        return self._tratar_resposta(resposta)

    def get(self, caminho: str, params: dict | None = None):
        return self._request("GET", caminho, params=params)

    def post(self, caminho: str, json_dados: dict | None = None):
        return self._request("POST", caminho, json=json_dados)

    def put(self, caminho: str, json_dados: dict | None = None):
        return self._request("PUT", caminho, json=json_dados)

    # ---- Autenticação ----

    def login(self, usuario: str, senha: str) -> dict:
        dados = self.post("/auth/login", {"usuario": usuario, "senha": senha})
        self.token = dados["access_token"]
        self.usuario_logado = self.get("/usuarios/me")
        return self.usuario_logado

    def logout(self):
        self.token = None
        self.usuario_logado = None

    # ---- Patrimônios ----

    def buscar_patrimonios(self, busca: str = "") -> list[dict]:
        params = {"busca": busca} if busca else None
        return self.get("/patrimonios", params=params)

    def obter_patrimonio(self, patrimonio_id: int) -> dict:
        return self.get(f"/patrimonios/{patrimonio_id}")

    def atualizar_patrimonio(self, patrimonio_id: int, dados: dict) -> dict:
        return self.put(f"/patrimonios/{patrimonio_id}", dados)

    # ---- Cadastros auxiliares (usados para preencher combos na ficha) ----

    def listar_itens(self) -> list[dict]:
        return self.get("/itens")

    def listar_secretarias(self) -> list[dict]:
        return self.get("/secretarias")

    def listar_setores(self, secretaria_id: int | None = None) -> list[dict]:
        params = {"secretaria_id": secretaria_id} if secretaria_id else None
        return self.get("/setores", params=params)

    def listar_locais(self, setor_id: int | None = None) -> list[dict]:
        params = {"setor_id": setor_id} if setor_id else None
        return self.get("/locais", params=params)

    def listar_empenhos(self) -> list[dict]:
        return self.get("/empenhos")

    def listar_aquisicoes(self) -> list[dict]:
        return self.get("/aquisicoes")

    def listar_fornecedores(self) -> list[dict]:
        return self.get("/fornecedores")

    # ---- Movimentações / Histórico ----

    def listar_movimentacoes(self, patrimonio_id: int) -> list[dict]:
        return self.get(f"/patrimonios/{patrimonio_id}/movimentacoes")

    def criar_movimentacao(self, patrimonio_id: int, dados: dict) -> dict:
        return self.post(f"/patrimonios/{patrimonio_id}/movimentacoes", dados)

    # ---- Manutenção ----

    def listar_manutencoes(self, patrimonio_id: int) -> list[dict]:
        return self.get(f"/patrimonios/{patrimonio_id}/manutencoes")

    def criar_manutencao(self, patrimonio_id: int, dados: dict) -> dict:
        return self.post(f"/patrimonios/{patrimonio_id}/manutencoes", dados)

    def atualizar_manutencao(self, patrimonio_id: int, manutencao_id: int, dados: dict) -> dict:
        return self.put(f"/patrimonios/{patrimonio_id}/manutencoes/{manutencao_id}", dados)

    # ---- Garantia ----

    def listar_garantias(self, patrimonio_id: int) -> list[dict]:
        return self.get(f"/patrimonios/{patrimonio_id}/garantias")

    def criar_garantia(self, patrimonio_id: int, dados: dict) -> dict:
        return self.post(f"/patrimonios/{patrimonio_id}/garantias", dados)

    def atualizar_garantia(self, patrimonio_id: int, garantia_id: int, dados: dict) -> dict:
        return self.put(f"/patrimonios/{patrimonio_id}/garantias/{garantia_id}", dados)

    def registrar_retorno_garantia(self, patrimonio_id: int, garantia_id: int, dados: dict) -> dict:
        return self.post(f"/patrimonios/{patrimonio_id}/garantias/{garantia_id}/retorno", dados)

    # ---- Anotações ----

    def listar_anotacoes(self, patrimonio_id: int) -> list[dict]:
        return self.get(f"/patrimonios/{patrimonio_id}/anotacoes")

    def criar_anotacao(self, patrimonio_id: int, texto: str) -> dict:
        return self.post(f"/patrimonios/{patrimonio_id}/anotacoes", {"texto": texto})

    # ---- Documentos ----

    def listar_documentos(self, patrimonio_id: int) -> list[dict]:
        return self.get(f"/patrimonios/{patrimonio_id}/documentos")

    def enviar_documento(self, patrimonio_id: int, tipo: str, caminho_local: str) -> dict:
        import os
        nome = os.path.basename(caminho_local)
        with open(caminho_local, "rb") as arquivo:
            try:
                resposta = requests.post(
                    f"{self.base_url}/patrimonios/{patrimonio_id}/documentos",
                    headers={"Authorization": f"Bearer {self.token}"} if self.token else {},
                    data={"tipo": tipo},
                    files={"arquivo": (nome, arquivo)},
                    timeout=30,
                )
            except requests.exceptions.RequestException as erro:
                raise ErroConexao(f"Não foi possível conectar ao servidor: {erro}") from erro
        return self._tratar_resposta(resposta)

    def baixar_documento(self, patrimonio_id: int, documento_id: int, destino_local: str) -> None:
        try:
            resposta = requests.get(
                f"{self.base_url}/patrimonios/{patrimonio_id}/documentos/{documento_id}/download",
                headers=self._headers(),
                timeout=30,
            )
        except requests.exceptions.RequestException as erro:
            raise ErroConexao(f"Não foi possível conectar ao servidor: {erro}") from erro
        if resposta.status_code >= 400:
            raise ErroAPI("Não foi possível baixar o documento.", resposta.status_code)
        with open(destino_local, "wb") as saida:
            saida.write(resposta.content)

    # ---- Relatórios ----

    def relatorio_patrimonio_geral(self) -> list[dict]:
        return self.get("/relatorios/patrimonio-geral")

    def relatorio_por_setor(self, setor_id: int | None = None) -> list[dict]:
        params = {"setor_id": setor_id} if setor_id else None
        return self.get("/relatorios/por-setor", params=params)

    def relatorio_por_fornecedor(self, fornecedor_id: int | None = None) -> list[dict]:
        params = {"fornecedor_id": fornecedor_id} if fornecedor_id else None
        return self.get("/relatorios/por-fornecedor", params=params)

    def relatorio_por_empenho(self, empenho_id: int | None = None) -> list[dict]:
        params = {"empenho_id": empenho_id} if empenho_id else None
        return self.get("/relatorios/por-empenho", params=params)

    def relatorio_incompletos(self) -> list[dict]:
        return self.get("/relatorios/incompletos")

    def relatorio_em_manutencao(self) -> list[dict]:
        return self.get("/relatorios/em-manutencao")

    def relatorio_em_garantia(self) -> list[dict]:
        return self.get("/relatorios/em-garantia")

    # ---- Dashboard / Pendências / Auditoria ----

    def resumo_dashboard(self) -> dict:
        return self.get("/dashboard/resumo")

    def resumo_pendencias(self) -> dict:
        return self.get("/pendencias/resumo")

    def listar_auditoria(self, patrimonio_id: int | None = None) -> list[dict]:
        params = {"patrimonio_id": patrimonio_id} if patrimonio_id else None
        return self.get("/auditoria", params=params)


# Instância única compartilhada pela aplicação inteira (uma sessão por usuário logado no PC).
cliente_api = ClienteAPI()
