# Arquitetura do Sistema — Olist SRE Pipeline

Este documento descreve a arquitetura do pipeline de dados da Olist utilizando o framework **RM-ODP** (Reference Model of Open Distributed Processing) e detalha as principais decisões arquiteturais (ADRs).

---

## 1. RM-ODP Viewpoints

### 1.1. Enterprise Viewpoint
Foca no propósito, escopo e políticas do sistema do ponto de vista do negócio.
- **Objetivo:** Garantir que o processamento de 100k pedidos diários seja confiável para a tomada de decisão.
- **Stakeholders:** Operação Olist, Time de Dados, SRE.
- **RFs Atendidos:** RF-01 até RF-08.
- **RNFs Atendidos:** Todos (Foco em RNF-01 e RNF-06).

### 1.2. Information Viewpoint
Define a estrutura dos dados e as transformações.
- **Modelo de Dados:**
  - **Bronze (Raw):** Arquivos CSV brutos ingeridos.
  - **Silver (Stage):** Tabelas espelho no PostgreSQL com tipos de dados validados.
  - **Gold (Analytical):** Tabelas agregadas e otimizadas para consumo no Grafana.
- **RFs Atendidos:** RF-01, RF-02, RF-03.
- **RNFs Atendidos:** RNF-01 (Integridade), RNF-08 (Segurança/PII).

### 1.3. Computational Viewpoint
Descreve a organização funcional do sistema através de objetos computacionais.
- **Injestor de Objetos:** Monitora e lê arquivos do S3/Local.
- **Carregador de Banco:** Gerencia transações e carga na camada Stage.
- **Motor de Transformação:** Executa queries SQL analíticas para popular a camada Gold.
- **Monitor de Saúde:** Emite métricas e logs para observabilidade.
- **RFs Atendidos:** RF-01, RF-02, RF-03, RF-07.
- **RNFs Atendidos:** RNF-02 (Performance), RNF-09 (Modularidade).

### 1.4. Engineering Viewpoint
Foca na infraestrutura de suporte e nos mecanismos de distribuição.
- **Pipeline Runner:** Instância EC2 executando scripts Python de ETL.
- **Database Engine:** Instância RDS (ou EC2 com Postgres) para persistência.
- **Observabilidade:** CloudWatch Logs/Metrics + Agente do Grafana.
- **Resiliência:** Uso de transações DB e logs de estado para idempotência e recuperação.
- **RFs Atendidos:** RF-04, RF-08.
- **RNFs Atendidos:** RNF-06 (Confiabilidade), RNF-07 (MTTR), RNF-10 (Portabilidade).

### 1.5. Technology Viewpoint
Especifica as tecnologias reais utilizadas (Considerando restrições AWS Academy).
- **Linguagem:** Python 3.9+ (com Pandas/SQLAlchemy).
- **Banco de Dados:** PostgreSQL 13+.
- **Infraestrutura:** AWS EC2 (t3.medium) para Aplicação e DB.
- **Monitoramento:** Grafana + CloudWatch.
- **RFs Atendidos:** Todos.
- **RNFs Atendidos:** RNF-02, RNF-03, RNF-04.

---

## 2. Architecture Decision Records (ADRs)

### ADR-01: Uso de Python no EC2 em vez de AWS Glue
- **Contexto:** Necessidade de processar 100k registros diários dentro das restrições do AWS Academy Learner Lab (onde o Glue não é permitido).
- **Decisão:** Utilizaremos scripts Python rodando em instâncias EC2 gerenciadas via Docker ou scripts shell.
- **Consequências:** Maior controle sobre o ambiente e custo zero de serviços gerenciados não permitidos, porém exige maior esforço de gerenciamento de infraestrutura (SRE).

### ADR-02: PostgreSQL como Data Warehouse Analítico
- **Contexto:** O projeto exige um banco analítico para alimentar dashboards, mas o AWS Redshift está fora de escopo e não é permitido no Learner Lab.
- **Decisão:** Utilizar o PostgreSQL com otimizações de índices e visualizações materializadas para atuar como nossa camada analítica (Gold).
- **Consequências:** Atende ao volume de 100k registros com facilidade, mas exige manutenção de índices e vácuo para manter a performance de RNF-02.

### ADR-03: Implementação de Idempotência via Camada Stage (Truncate-Load)
- **Contexto:** Garantir RF-04 e RNF-01 em caso de reprocessamento ou falhas parciais.
- **Decisão:** A cada run, a camada de Stage para o período específico será limpa (Truncate/Delete) antes da nova carga, e as transformações para a camada Gold usarão UPSERT ou substituição de partição lógica.
- **Consequências:** Garante que o estado final seja consistente independente de falhas no meio do processo, atendendo à propriedade de idempotência.

---

## 3. Mapeamento Componente x Requisitos

| Componente | RFs Atendidos | RNFs Atendidos |
| :--- | :--- | :--- |
| **Python ETL Script** | RF-01, RF-02, RF-03 | RNF-02, RNF-09 |
| **PostgreSQL (Stage/Gold)** | RF-02, RF-03, RF-04 | RNF-01, RNF-04 |
| **Grafana Dashboard** | RF-05 | RNF-03, RNF-05 |
| **CloudWatch / Logs** | RF-07 | RNF-06, RNF-08 |
| **Docker / IaC** | RF-08 | RNF-10, RNF-07 |
