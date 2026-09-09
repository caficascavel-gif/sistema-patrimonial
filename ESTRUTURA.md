# Estrutura de Pastas — Sistema de Controle Patrimonial

```
patrimonio-sistema/
│
├── backend/                        # API FastAPI (roda no servidor)
│   ├── app/
│   │   ├── main.py                 # ponto de entrada da API
│   │   ├── config.py                # leitura de variáveis de ambiente (.env)
│   │   ├── database.py              # conexão SQLAlchemy + sessão
│   │   ├── security.py              # hash de senha, JWT
│   │   │
│   │   ├── models/                  # modelos SQLAlchemy (1 arquivo por entidade)
│   │   │   ├── usuario.py
│   │   │   ├── perfil.py
│   │   │   ├── secretaria.py
│   │   │   ├── setor.py
│   │   │   ├── local.py
│   │   │   ├── categoria.py
│   │   │   ├── item.py
│   │   │   ├── marca.py
│   │   │   ├── modelo.py
│   │   │   ├── fornecedor.py
│   │   │   ├── empenho.py
│   │   │   ├── aquisicao.py
│   │   │   ├── patrimonio.py
│   │   │   ├── movimentacao.py
│   │   │   ├── manutencao.py
│   │   │   ├── garantia.py
│   │   │   ├── anotacao.py
│   │   │   ├── documento.py
│   │   │   └── auditoria.py
│   │   │
│   │   ├── schemas/                 # Pydantic (validação/serialização) — mesma divisão
│   │   │
│   │   ├── routers/                 # rotas da API — 1 arquivo por recurso
│   │   │   ├── auth.py
│   │   │   ├── usuarios.py
│   │   │   ├── patrimonios.py
│   │   │   ├── movimentacoes.py
│   │   │   ├── manutencoes.py
│   │   │   ├── garantias.py
│   │   │   ├── anotacoes.py
│   │   │   ├── documentos.py
│   │   │   ├── cadastros.py         # fornecedores, empenhos, itens, locais etc.
│   │   │   ├── relatorios.py
│   │   │   ├── dashboard.py
│   │   │   └── auditoria.py
│   │   │
│   │   └── utils/
│   │       ├── permissoes.py        # checagem de perfil x ação
│   │       └── pendencias.py        # cálculo de cadastro incompleto
│   │
│   ├── alembic/                     # migrações do banco (versionamento de schema)
│   ├── requirements.txt
│   └── .env.example
│
├── client/                          # Aplicação desktop PySide6 (roda em cada PC)
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py                 # endereço da API, salvo localmente
│   │   ├── api_client.py             # camada HTTP -> nunca acessa o MySQL direto
│   │   ├── auth/
│   │   │   └── login_window.py
│   │   ├── ui/
│   │   │   ├── main_window.py        # tela principal (pesquisa + resultados)
│   │   │   ├── ficha_patrimonio/     # janela modal com abas
│   │   │   │   ├── ficha_window.py
│   │   │   │   ├── aba_cadastro.py
│   │   │   │   ├── aba_historico.py
│   │   │   │   ├── aba_movimentacoes.py
│   │   │   │   ├── aba_manutencao.py
│   │   │   │   ├── aba_garantia.py
│   │   │   │   ├── aba_anotacoes.py
│   │   │   │   └── aba_documentos.py
│   │   │   ├── cadastros_admin/      # telas de fornecedores, itens, locais...
│   │   │   ├── dashboard.py
│   │   │   └── relatorios.py
│   │   └── resources/                # ícones, estilos (qss)
│   ├── requirements.txt
│   └── build/
│       ├── patrimonio.spec           # PyInstaller
│       └── installer.iss             # Inno Setup
│
├── database/
│   ├── schema.sql                    # DDL completo (criação das tabelas)
│   └── seed_exemplo.sql              # dados de teste (Etapa 1, opcional)
│
└── docs/
    └── plano_implementacao.md
```

**Regra de comunicação:** o cliente (PySide6) nunca acessa o MySQL diretamente — só fala com a API via HTTP/REST. Isso resolve o requisito de rede/intranet e mantém as credenciais do banco só no servidor.
