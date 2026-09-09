-- =========================================================
-- SISTEMA DE CONTROLE PATRIMONIAL E EQUIPAMENTOS
-- Schema MySQL — Etapa 1
-- =========================================================

CREATE DATABASE IF NOT EXISTS patrimonio_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE patrimonio_db;

-- =========================================================
-- ACESSO / USUÁRIOS
-- =========================================================

CREATE TABLE perfis (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  nome          VARCHAR(60) NOT NULL UNIQUE,   -- Administrador, Patrimônio, Administrativo/Compras, Engenharia Clínica, Consulta
  descricao     VARCHAR(255),
  ativo         TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB;

CREATE TABLE secretarias (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  nome          VARCHAR(150) NOT NULL UNIQUE,
  ativo         TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB;

CREATE TABLE setores (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  secretaria_id   INT NOT NULL,
  nome            VARCHAR(150) NOT NULL,
  ativo           TINYINT(1) NOT NULL DEFAULT 1,
  FOREIGN KEY (secretaria_id) REFERENCES secretarias(id),
  UNIQUE KEY uq_setor (secretaria_id, nome)
) ENGINE=InnoDB;

CREATE TABLE locais (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  setor_id      INT NOT NULL,
  nome          VARCHAR(150) NOT NULL,      -- ex: "Sala de Equipamentos", "Consultório 01"
  ativo         TINYINT(1) NOT NULL DEFAULT 1,
  FOREIGN KEY (setor_id) REFERENCES setores(id),
  UNIQUE KEY uq_local (setor_id, nome)
) ENGINE=InnoDB;

CREATE TABLE usuarios (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  nome            VARCHAR(150) NOT NULL,
  usuario         VARCHAR(60) NOT NULL UNIQUE,
  senha_hash      VARCHAR(255) NOT NULL,
  perfil_id       INT NOT NULL,
  secretaria_id   INT,
  setor_id        INT,
  ativo           TINYINT(1) NOT NULL DEFAULT 1,
  criado_em       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (perfil_id) REFERENCES perfis(id),
  FOREIGN KEY (secretaria_id) REFERENCES secretarias(id),
  FOREIGN KEY (setor_id) REFERENCES setores(id)
) ENGINE=InnoDB;

-- =========================================================
-- CADASTROS BASE (reutilizáveis)
-- =========================================================

CREATE TABLE categorias (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  nome          VARCHAR(120) NOT NULL UNIQUE,
  ativo         TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB;

CREATE TABLE marcas (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  nome          VARCHAR(120) NOT NULL UNIQUE,
  ativo         TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB;

CREATE TABLE modelos (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  marca_id      INT NOT NULL,
  nome          VARCHAR(120) NOT NULL,
  ativo         TINYINT(1) NOT NULL DEFAULT 1,
  FOREIGN KEY (marca_id) REFERENCES marcas(id),
  UNIQUE KEY uq_modelo (marca_id, nome)
) ENGINE=InnoDB;

CREATE TABLE fornecedores (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  razao_social    VARCHAR(200) NOT NULL,
  nome_fantasia   VARCHAR(200),
  cnpj            VARCHAR(20) UNIQUE,
  telefone        VARCHAR(30),
  email           VARCHAR(150),
  endereco        VARCHAR(255),
  contato         VARCHAR(150),
  observacoes     TEXT,
  ativo           TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB;

-- =========================================================
-- ITEM / EQUIPAMENTO (o "tipo" de equipamento)
-- =========================================================

CREATE TABLE itens (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  descricao       VARCHAR(200) NOT NULL,      -- ex: "Fotopolimerizador"
  categoria_id    INT,
  marca_id        INT,
  modelo_id       INT,
  fabricante      VARCHAR(150),
  caracteristicas TEXT,
  observacoes     TEXT,
  ativo           TINYINT(1) NOT NULL DEFAULT 1,
  FOREIGN KEY (categoria_id) REFERENCES categorias(id),
  FOREIGN KEY (marca_id) REFERENCES marcas(id),
  FOREIGN KEY (modelo_id) REFERENCES modelos(id)
) ENGINE=InnoDB;

-- =========================================================
-- EMPENHO / AQUISIÇÃO (a "compra")
-- =========================================================

CREATE TABLE empenhos (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  numero          VARCHAR(40) NOT NULL,       -- ex: "6672"
  ano             INT NOT NULL,                -- ex: 2026
  fornecedor_id   INT,
  processo        VARCHAR(60),                 -- processo/licitação
  data            DATE,
  valor           DECIMAL(14,2),
  observacoes     TEXT,
  FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id),
  UNIQUE KEY uq_empenho (numero, ano)
) ENGINE=InnoDB;

CREATE TABLE aquisicoes (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  fornecedor_id   INT,
  empenho_id      INT,
  nota_fiscal     VARCHAR(60),
  data_compra     DATE,
  data_entrada    DATE,
  valor           DECIMAL(14,2),
  observacoes     TEXT,
  FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id),
  FOREIGN KEY (empenho_id) REFERENCES empenhos(id)
) ENGINE=InnoDB;

CREATE TABLE documentos_empenho (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  empenho_id      INT NOT NULL,
  nome_arquivo    VARCHAR(255) NOT NULL,
  caminho         VARCHAR(500) NOT NULL,
  enviado_em      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  usuario_id      INT,
  FOREIGN KEY (empenho_id) REFERENCES empenhos(id),
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
) ENGINE=InnoDB;

-- =========================================================
-- PATRIMÔNIO (o bem físico individual)
-- =========================================================

CREATE TABLE patrimonios (
  id                INT AUTO_INCREMENT PRIMARY KEY,
  numero_patrimonio VARCHAR(40) NOT NULL UNIQUE,   -- ex: "359036"
  ipm               VARCHAR(40),
  item_id           INT NOT NULL,
  numero_serie      VARCHAR(100),
  aquisicao_id      INT,
  empenho_id        INT,

  -- localização atual (desnormalizado por performance; a verdade histórica vive em movimentacoes)
  secretaria_id     INT,
  setor_id          INT,
  local_id          INT,
  responsavel_id    INT,             -- FK usuarios, opcional

  situacao_atual    ENUM('Em uso','Disponível','Em manutenção','Em garantia',
                          'Emprestado','Baixado','Descartado') NOT NULL DEFAULT 'Disponível',

  criado_em         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  atualizado_em     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  FOREIGN KEY (item_id) REFERENCES itens(id),
  FOREIGN KEY (aquisicao_id) REFERENCES aquisicoes(id),
  FOREIGN KEY (empenho_id) REFERENCES empenhos(id),
  FOREIGN KEY (secretaria_id) REFERENCES secretarias(id),
  FOREIGN KEY (setor_id) REFERENCES setores(id),
  FOREIGN KEY (local_id) REFERENCES locais(id),
  FOREIGN KEY (responsavel_id) REFERENCES usuarios(id),
  INDEX idx_patrimonio_numero (numero_patrimonio),
  INDEX idx_patrimonio_ipm (ipm),
  INDEX idx_patrimonio_serie (numero_serie)
) ENGINE=InnoDB;

-- =========================================================
-- MOVIMENTAÇÕES / HISTÓRICO (nunca apagar / nunca sobrescrever)
-- =========================================================

CREATE TABLE movimentacoes (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  patrimonio_id   INT NOT NULL,
  data            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  tipo            ENUM('Entrada','Transferência','Empréstimo','Engenharia Clínica',
                        'Manutenção','Garantia','Retorno de garantia',
                        'Retorno de manutenção','Baixa','Descarte','Outros') NOT NULL,
  origem          VARCHAR(200),
  destino         VARCHAR(200),
  responsavel_id  INT NOT NULL,
  motivo          VARCHAR(255),
  observacao      TEXT,
  FOREIGN KEY (patrimonio_id) REFERENCES patrimonios(id),
  FOREIGN KEY (responsavel_id) REFERENCES usuarios(id),
  INDEX idx_mov_patrimonio (patrimonio_id, data)
) ENGINE=InnoDB;

-- =========================================================
-- MANUTENÇÃO
-- =========================================================

CREATE TABLE manutencoes (
  id                INT AUTO_INCREMENT PRIMARY KEY,
  patrimonio_id     INT NOT NULL,
  data              DATE NOT NULL,
  problema_relatado TEXT,
  responsavel_id    INT,
  servico_realizado TEXT,
  pecas_utilizadas  TEXT,
  custo             DECIMAL(14,2),
  fornecedor_id     INT,
  situacao          ENUM('Em análise','Em manutenção','Aguardando peça',
                          'Aguardando fornecedor','Resolvido','Sem conserto',
                          'Encaminhado para garantia') NOT NULL DEFAULT 'Em análise',
  conclusao         TEXT,
  observacoes       TEXT,
  FOREIGN KEY (patrimonio_id) REFERENCES patrimonios(id),
  FOREIGN KEY (responsavel_id) REFERENCES usuarios(id),
  FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id)
) ENGINE=InnoDB;

-- =========================================================
-- GARANTIA
-- =========================================================

CREATE TABLE garantias (
  id                  INT AUTO_INCREMENT PRIMARY KEY,
  patrimonio_id       INT NOT NULL,
  fornecedor_id       INT,
  data_envio          DATE,
  protocolo           VARCHAR(80),
  motivo              VARCHAR(255),
  problema            TEXT,
  previsao_retorno    DATE,
  situacao            ENUM('Aguardando envio','Enviado','Aguardando fornecedor',
                            'Em análise','Concluído','Retornado','Sem solução')
                       NOT NULL DEFAULT 'Aguardando envio',
  observacoes         TEXT,
  movimentacao_retorno_id INT,        -- preenchido quando o retorno é registrado
  FOREIGN KEY (patrimonio_id) REFERENCES patrimonios(id),
  FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id),
  FOREIGN KEY (movimentacao_retorno_id) REFERENCES movimentacoes(id)
) ENGINE=InnoDB;

-- =========================================================
-- ANOTAÇÕES (append-only)
-- =========================================================

CREATE TABLE anotacoes (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  patrimonio_id   INT NOT NULL,
  usuario_id      INT NOT NULL,
  data_hora       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  texto           TEXT NOT NULL,
  FOREIGN KEY (patrimonio_id) REFERENCES patrimonios(id),
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
) ENGINE=InnoDB;

-- =========================================================
-- DOCUMENTOS
-- =========================================================

CREATE TABLE documentos (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  patrimonio_id   INT NOT NULL,
  tipo            ENUM('Nota Fiscal','Empenho','Termo de garantia','Ordem de serviço',
                        'Laudo técnico','Comunicação do fornecedor','Outros') NOT NULL,
  nome_arquivo    VARCHAR(255) NOT NULL,
  caminho         VARCHAR(500) NOT NULL,     -- caminho/URL no armazenamento do servidor
  enviado_em      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  usuario_id      INT,
  FOREIGN KEY (patrimonio_id) REFERENCES patrimonios(id),
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
) ENGINE=InnoDB;

-- =========================================================
-- AUDITORIA
-- =========================================================

CREATE TABLE auditoria (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id      INT NOT NULL,
  data_hora       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  patrimonio_id   INT,
  entidade        VARCHAR(60) NOT NULL,      -- ex: 'patrimonio', 'fornecedor'
  entidade_id     INT NOT NULL,
  acao            VARCHAR(60) NOT NULL,      -- ex: 'update_localizacao'
  campo           VARCHAR(80),
  valor_anterior  TEXT,
  valor_novo      TEXT,
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
  FOREIGN KEY (patrimonio_id) REFERENCES patrimonios(id),
  INDEX idx_auditoria_patrimonio (patrimonio_id, data_hora)
) ENGINE=InnoDB;

-- =========================================================
-- SEED MÍNIMO — perfis padrão
-- =========================================================

INSERT INTO perfis (nome, descricao) VALUES
  ('Administrador', 'Acesso completo'),
  ('Patrimônio', 'Cadastro e gerenciamento de patrimônios e movimentações'),
  ('Administrativo/Compras', 'Cadastro de fornecedores, empenhos e aquisições'),
  ('Engenharia Clínica', 'Manutenção, garantia e informações técnicas'),
  ('Consulta', 'Somente visualização e relatórios');
