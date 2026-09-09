# Guia Único — Sistema de Controle Patrimonial (versão gratuita, zero instalação)

Este é o **único** guia a seguir, do começo ao fim. Nada aqui exige
instalar programa nenhum no seu PC pessoal (os `.exe` Windows são gerados
na nuvem, de graça, pelo GitHub) — só o PC "ponto" recebe arquivos prontos.

**Não existe mais nenhuma etapa de Python/venv na sua máquina.** Se você
está vendo isso em algum lugar, é resquício de versão antiga — ignore.

---

## Visão geral

```
Seu celular / PC de qualquer usuário
        │  (internet)
        ▼
patrimonio.seusubdominio.algumacoisa  ← endereço público (via FreeDNS)
        │
        ▼
Cloudflare Tunnel
        │
        ▼
PC "ponto"  (liga 07h, desliga 19h)
   ├─ MySQL portátil
   ├─ API do sistema (.exe)
   └─ Cloudflare Tunnel (.exe)
```

---

## PARTE 1 — MySQL portátil (só baixar e extrair)

1. https://dev.mysql.com/downloads/mysql/ → **Windows** → baixe o arquivo
   **"ZIP Archive"** (não o "MSI Installer").
2. Crie `C:\PatrimonioPortatil\`.
3. Extraia o ZIP, renomeie a pasta extraída pra `mysql`, mova pra dentro de
   `C:\PatrimonioPortatil\`.
4. Confirme: `C:\PatrimonioPortatil\mysql\bin\mysqld.exe` existe.
5. Pegue o `my.ini` (pasta `mysql-portatil/` do zip) e copie pra
   `C:\PatrimonioPortatil\mysql\`.

Só isso — nada de comando ainda.

---

## PARTE 2 — Gerar os 4 programas Windows (pelo navegador, sem instalar nada)

O GitHub compila os `.exe` pra você, de graça, numa máquina Windows na
nuvem dele. Você só sobe os arquivos do projeto e baixa o resultado. **Não
precisa ter Python, nem nada, instalado no seu computador para esta parte.**

### 2.1. Criar conta no GitHub (grátis, na hora)

https://github.com/signup — só e-mail e senha, sem cartão.

### 2.2. Criar um repositório novo

1. Clique no **+** no canto superior direito → **New repository**.
2. Nome: `sistema-patrimonial` (ou o que preferir).
3. Marque **Public**.
4. **Create repository**.

### 2.3. Subir os arquivos do projeto

1. Na página do repositório vazio, clique em **"uploading an existing
   file"** (ou "Add file" → "Upload files").
2. Extraia o zip que te mandei no seu computador. Arraste **todo o
   conteúdo** da pasta (as pastas `backend`, `instalador`, `database`,
   `client`, `.github`, etc. — tudo que está dentro da pasta
   `patrimonio-sistema`) pra dentro da área de upload do navegador.
   > O GitHub, pelo navegador, não mostra pastas ocultas como `.github`
   > durante o arraste em alguns sistemas operacionais. Se depois do
   > commit você não vir a pasta `.github/workflows/build.yml` na lista de
   > arquivos do repositório, siga o passo 2.4 abaixo mesmo assim — ele
   > cria o arquivo direto pelo navegador, sem depender do arraste.
3. Role até embaixo, clique **Commit changes**.

### 2.4. Conferir/criar o arquivo que manda o GitHub compilar

1. Na página do repositório, veja se já existe o caminho
   `.github/workflows/build.yml` (clique em `.github` → `workflows`).
2. **Se já existir**, pule pro passo 2.5.
3. **Se não existir**: clique em **Add file** → **Create new file**. No
   campo do nome do arquivo, digite exatamente:
   `.github/workflows/build.yml`
   (as barras fazem ele criar as pastas sozinho). Abra o arquivo
   `.github/workflows/build.yml` que está no zip (num editor de texto),
   copie **todo o conteúdo**, cole na caixa de texto grande do GitHub, e
   clique **Commit changes**.

### 2.5. Ver ele compilar sozinho

1. Clique na aba **Actions** (topo da página do repositório).
2. Deve aparecer uma execução chamada "Gerar programas Windows" rodando
   (bolinha amarela). Espere uns 3-5 minutos até virar um ✅ verde.
3. Clique nela. Bem embaixo da página, tem uma seção **Artifacts** com um
   arquivo `programas-windows` — clique pra baixar (vem um `.zip`).

### 2.6. Distribuir os programas nas pastas certas

Extraia esse `.zip` baixado. Dentro tem 4 arquivos `.exe` (cada um é um
arquivo único, não uma pasta). Distribua assim:

```
C:\PatrimonioPortatil\
  ├─ mysql\                     (já está aqui, da Parte 1)
  ├─ api\
  │   └─ SistemaPatrimonialAPI.exe
  ├─ ConfigurarTudo\
  │   └─ ConfigurarTudo.exe
  ├─ IniciarSistema\
  │   └─ IniciarSistema.exe
  └─ PararSistema\
      └─ PararSistema.exe
```

(crie essas 4 pastinhas e coloque cada `.exe` na sua, exatamente como
mostrado acima).

---

## PARTE 3 — Rodar o Configurador (uma vez só)

Dê **dois cliques** em `C:\PatrimonioPortatil\ConfigurarTudo\ConfigurarTudo.exe`.

Ele sozinho inicializa o MySQL, define as senhas, cria as tabelas, e gera
o `.env` da API. No final, pergunta:

- Nome completo
- Usuário (login)
- Senha

Isso cria o primeiro Administrador — **guarde esse login**.

> As senhas geradas pro banco ficam salvas em
> `C:\PatrimonioPortatil\SENHAS_GERADAS_NAO_PERDER.txt` (só por segurança,
> não precisa delas no dia a dia).

Rodar de novo não duplica nada — ele percebe que já está pronto.

---

## PARTE 4 — Endereço público (FreeDNS + Cloudflare — libera na hora)

**Não use eu.org.** A fila de aprovação manual de lá pode levar dias. O
caminho abaixo (FreeDNS) libera o subdomínio na hora, sem esperar
aprovação de ninguém.

### 4.1. Pegar um subdomínio grátis e instantâneo no FreeDNS

1. https://freedns.afraid.org → crie conta (instantâneo, sem aprovação).
2. Depois de logado, clique em **Subdomains** → **Add**.
3. Em **Domain**, clique em "many many more available..." e escolha
   qualquer um da lista (ex: `mooo.com`, `strangled.net`).
4. Em **Subdomain**, digite algo como `patrimoniocascavel`.
5. Por enquanto, em **Destination**, coloque qualquer IP temporário (ex:
   `1.1.1.1`) — vamos trocar já já. Salve.

Seu endereço vai ser algo como `patrimoniocascavel.mooo.com`.

### 4.2. Criar conta na Cloudflare e adicionar esse domínio

1. https://dash.cloudflare.com/sign-up (grátis, sem cartão).
2. **Add a Site** → digite `patrimoniocascavel.mooo.com` (o endereço
   completo que você criou no FreeDNS) → plano **Free**.
3. Pule a checagem de DNS existente.
4. A Cloudflare mostra **2 nameservers** (tipo `liz.ns.cloudflare.com`) —
   anote os dois.

### 4.3. Voltar no FreeDNS e apontar pra Cloudflare de vez

1. No FreeDNS, edite o registro que você criou no passo 4.1.
2. Troque o **Type** de A pra **NS**, e no lugar do IP temporário, coloque
   um dos 2 nameservers da Cloudflare. Salve.
3. Repita criando **outro** registro NS igual, com o segundo nameserver.

Isso costuma propagar em minutos. Volte no painel da Cloudflare até o
status do site virar **"Active"**.

---

## PARTE 5 — Cloudflare Tunnel (sem instalador)

1. https://github.com/cloudflare/cloudflared/releases/latest → baixe
   **`cloudflared-windows-amd64.exe`** (não o `.msi`) → renomeie pra
   `cloudflared.exe`.
2. Crie `C:\PatrimonioPortatil\cloudflare\` e coloque ele lá.
3. Prompt de Comando nessa pasta:
   ```
   cloudflared.exe tunnel login
   ```
   (escolha o domínio no navegador que abrir, confirme).
   ```
   cloudflared.exe tunnel create patrimonio
   ```
   Anote o **Tunnel ID**. Copie o `<TUNNEL-ID>.json` gerado (está em
   `C:\Users\SeuUsuario\.cloudflared\`) pra dentro de
   `C:\PatrimonioPortatil\cloudflare\`.
4. Pegue o `config.yml` (pasta `cloudflare-tunnel/` do zip), copie pra lá,
   edite trocando `PREENCHER-DEPOIS-COM-O-TUNNEL-ID` (2 vezes) e o
   endereço pelo seu domínio real (`patrimoniocascavel.mooo.com`).
5. ```
   cloudflared.exe tunnel route dns patrimonio patrimoniocascavel.mooo.com
   ```

---

## PARTE 6 — Testar tudo junto

Dê dois cliques em `C:\PatrimonioPortatil\IniciarSistema\IniciarSistema.exe`.
3 janelas devem abrir (MySQL, API, Tunnel).

No celular, com **wi-fi desligado** (só 4G/5G), abra:
`https://patrimoniocascavel.mooo.com/app/`

Deve aparecer a tela de login.

Pra desligar tudo: `PararSistema.exe`.

---

## PARTE 7 — Página "porteira"

1. Abra `pagina-porteira/index.html` (do zip), troque `URL_SISTEMA` pelo
   seu endereço real terminando em `/app/`.
2. Painel Cloudflare → **Workers & Pages** → **Create** → **Pages** →
   **Upload assets** → arraste esse `index.html` → **Deploy**.
3. O endereço que ele der (tipo `patrimonio-porteira.pages.dev`) é o que
   você divulga pros usuários.

---

## PARTE 8 — Teste funcional completo

Com `IniciarSistema.exe` rodando, abra o sistema e siga, na ordem:

1. **Login** — entre, erre a senha uma vez de propósito.
2. **Cadastros** (🗂️) — Categoria, Item, Secretaria, Setor, Local, Fornecedor.
3. **Pesquisar** → **+ Novo patrimônio**.
4. **Aba Cadastro** → Editar → preencher → Salvar.
5. **Aba Movimentações** → Nova Movimentação → confirme no Histórico.
6. **Aba Manutenção** → Registrar → mudar situação.
7. **Aba Garantia** → Registrar envio → **REGISTRAR RETORNO** → confirme
   movimentação automática.
8. **Aba Anotações** e **Documentos**.
9. **Anterior/Próximo**, e fechar sem salvar (deve avisar).
10. **Relatórios** → CSV → imprimir.
11. **Dashboard** → clicar numa pendência.
12. **Auditoria** → conferir a edição do passo 4.
13. **Usuários** → criar um "Consulta" → testar permissões.

---

## PARTE 9 — Levar pro PC "ponto"

Teste antes um `.exe` solto qualquer nesse PC, só pra confirmar.

1. Copie `C:\PatrimonioPortatil\` inteira, **mesmo caminho exato**, pro PC
   "ponto".
2. Rode `IniciarSistema.exe` lá manualmente uma vez, confirme que abre.
3. Teste pelo endereço público.
4. `Windows + R` → `shell:startup` → crie um atalho de `IniciarSistema.exe`
   nessa pasta.

---

## Solução de problemas comuns

**GitHub Actions deu ❌ vermelho em vez de ✅**
Clique na execução, depois no passo que falhou (fica marcado), e me cole
aqui a mensagem de erro em vermelho.

**"Access denied for user 'root'@'localhost'" no Configurador**
Apague tudo dentro de `C:\PatrimonioPortatil\mysql\data\` e rode o
`ConfigurarTudo.exe` de novo do zero.

**"Não foi possível conectar ao servidor"**
Confira as 3 janelas abertas sem erro. Teste `http://localhost:8000`
primeiro.

**Antivírus bloqueia/apaga algum `.exe` sozinho**
Se for quarentena/apagar (não um aviso liberável), me avise — a solução
muda.

**Token expira depois de 8h**
Esperado — a tela manda pro login sozinha.
