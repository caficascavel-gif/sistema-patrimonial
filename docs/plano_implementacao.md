# Plano de Implementação

## Observação sobre o ambiente de desenvolvimento
Todo o código (backend FastAPI, cliente PySide6, schema MySQL, spec do PyInstaller, script do Inno Setup) será gerado como código-fonte real, testável. Duas partes, porém, exigem um ambiente que eu não tenho aqui:
- **Rodar o MySQL "de verdade" acessível pela rede** — preciso que você suba o servidor MySQL (local ou no servidor da Prefeitura) e me passe as credenciais/endereço para testarmos a API contra ele, ou você mesmo testa localmente com as instruções que eu fornecer.
- **Gerar o `.exe`/instalador Windows final** — PyInstaller e Inno Setup precisam rodar em Windows. Eu entrego o `.spec` e o `.iss` prontos; a geração do instalador final é executada na sua máquina Windows (posso te guiar passo a passo).

## Etapas
| Etapa | Entregável |
|---|---|
| 1 | Estrutura de pastas + schema MySQL + plano ✅ (este documento) |
| 2 | Backend: conexão ao banco, login (JWT), CRUD de usuários/perfis |
| 3 | Backend + cliente: cadastros básicos (categorias, marcas, modelos, fornecedores, secretarias/setores/locais, itens) |
| 4 | Backend + cliente: cadastro de patrimônio (com suporte a cadastro parcial e indicador 🟢/🟡) |
| 5 | Cliente: tela de pesquisa + lista de resultados |
| 6 | Cliente: ficha do patrimônio (modal, abas, navegação anterior/próximo) |
| 7 | Movimentações + histórico (linha do tempo) |
| 8 | Manutenção + garantia (com geração automática de movimentação no retorno) |
| 9 | Anotações + documentos (upload) |
| 10 | Relatórios (tela, impressão, exportação PDF/Excel) |
| 11 | Auditoria + pendências + dashboard |
| 12 | Build: PyInstaller (.exe) + Inno Setup (instalador) + tela de configuração do endereço da API |

Cada etapa será entregue com código funcional e testável antes de avançar para a próxima, conforme pedido.

## Próximo passo
Etapa 2: login e usuários. Preciso confirmar duas decisões técnicas simples antes de codar:
1. Autenticação: JWT com expiração (ex: 8h, renovando ao usar o sistema) — ok?
2. Onde salvar os arquivos de documentos (Etapa 9, mas afeta a estrutura): pasta compartilhada de rede no servidor, ou isso ainda não está definido? Pode ficar em aberto por enquanto — uso um caminho local placeholder e ajustamos depois.
