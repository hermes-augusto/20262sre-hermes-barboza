# Especificação de Requisitos Não Funcionais (RNF) — Olist SRE Pipeline

## 1. Introdução
Este documento define os requisitos não funcionais para o pipeline de dados da Olist, baseando-se nos atributos de qualidade da norma **ISO 25010**. O objetivo é garantir que o sistema opere com alta performance, confiabilidade e operabilidade.

## 2. Metodologia
- **ISO 25010:** Estrutura para categorização de atributos de qualidade.
- **SLI/SLO:** Definição de indicadores e objetivos de nível de serviço mensuráveis.
- **MoSCoW:** Priorização dos requisitos.

---

## 3. Atributos de Qualidade (ISO 25010)

### 3.1. Adequação Funcional (Functional Suitability)
- **RNF-01: Integridade dos Dados de Ingestão**
  - **Descrição:** O sistema deve garantir que nenhum registro seja perdido entre a origem (CSV) e o banco analítico.
  - **SLI:** Razão entre registros na tabela analítica final e registros no CSV de origem (ajustado por regras de negócio).
  - **SLO:** 100% de integridade para arquivos válidos.
  - **Prioridade:** Must (Essencial)

### 3.2. Eficiência de Performance (Performance Efficiency)
- **RNF-02: Tempo de Processamento do Pipeline**
  - **Descrição:** O pipeline deve processar o volume diário de 100 mil pedidos dentro de uma janela operacional aceitável.
  - **SLI:** Tempo total de execução (End-to-End) por lote diário.
  - **SLO:** < 60 minutos para 100.000 registros em uma instância EC2 t3.medium.
  - **Prioridade:** Must (Essencial)

- **RNF-03: Latência de Atualização do Dashboard**
  - **Descrição:** Os dados devem estar disponíveis para visualização logo após a conclusão do processamento.
  - **SLI:** Tempo entre a escrita final no Postgres e a disponibilidade do dado no Grafana.
  - **SLO:** < 5 minutos (P95).
  - **Prioridade:** Should (Importante)

### 3.3. Compatibilidade (Compatibility)
- **RNF-04: Coexistência com PostgreSQL**
  - **Descrição:** O pipeline deve ser compatível com as versões 13+ do PostgreSQL.
  - **SLI:** Sucesso de conexão e execução de queries DDL/DML.
  - **SLO:** 100% de compatibilidade em ambiente de staging/produção.
  - **Prioridade:** Must (Essencial)

### 3.4. Usabilidade (Usability)
- **RNF-05: Clareza Visual de Status**
  - **Descrição:** Operadores devem conseguir identificar o status da última execução em menos de 10 segundos ao abrir o Grafana.
  - **SLI:** Presença de indicadores de status (Semáforo: Verde/Amarelo/Vermelho) no topo do dashboard.
  - **SLO:** Disponibilidade visual de status de 99.9%.
  - **Prioridade:** Should (Importante)

### 3.5. Confiabilidade (Reliability)
- **RNF-06: Taxa de Sucesso do Pipeline**
  - **Descrição:** O pipeline deve concluir suas execuções com sucesso, minimizando intervenções manuais.
  - **SLI:** Porcentagem de execuções finalizadas com status "Success".
  - **SLO:** > 98% de sucesso em uma janela móvel de 30 dias.
  - **Prioridade:** Must (Essencial)

- **RNF-07: Recuperação de Falhas (MTTR)**
  - **Descrição:** O tempo para recuperar o sistema após uma falha crítica de infraestrutura deve ser minimizado.
  - **SLI:** Tempo médio de recuperação (Mean Time To Recovery).
  - **SLO:** < 2 horas para recuperação de dados em caso de falha de hardware/instância.
  - **Prioridade:** Should (Importante)

### 3.6. Segurança (Security)
- **RNF-08: Proteção de Dados Sensíveis (LGPD)**
  - **Descrição:** O pipeline não deve expor dados sensíveis de clientes nos logs ou em tabelas analíticas sem necessidade.
  - **SLI:** Auditoria automatizada de campos em logs e tabelas.
  - **SLO:** Zero PII (Personally Identifiable Information) em logs de erro ou tabelas de stage analíticas.
  - **Prioridade:** Must (Essencial)

### 3.7. Manutenibilidade (Maintainability)
- **RNF-09: Modularidade do ETL**
  - **Descrição:** Alterações em uma etapa (ex: Ingestão) não devem afetar a lógica de outra (ex: Transformação).
  - **SLI:** Cobertura de testes unitários por módulo.
  - **SLO:** > 80% de cobertura de código em lógica de transformação.
  - **Prioridade:** Should (Importante)

### 3.8. Portabilidade (Portability)
- **RNF-10: Facilidade de Instalação (Infrastructure as Code)**
  - **Descrição:** O ambiente do pipeline deve ser replicável via automação.
  - **SLI:** Tempo para subir um novo ambiente completo (BD + App + Dashboard).
  - **SLO:** < 30 minutos utilizando scripts IaC/Docker.
  - **Prioridade:** Could (Desejável)

---

## 4. Tabela Resumo (SLI/SLO e Prioridade)

| ID | Atributo ISO 25010 | SLI | SLO | Fonte de Medição | Prioridade |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **RNF-01** | Adequação Funcional | Razão de Integridade | 100% | Logs de Auditoria / DB | Must |
| **RNF-02** | Performance | Tempo de Execução | < 60 min | CloudWatch / Logs | Must |
| **RNF-03** | Performance | Latência Dash | < 5 min | Observabilidade Dash | Should |
| **RNF-04** | Compatibilidade | Sucesso SQL | 100% | Logs de Aplicação | Must |
| **RNF-05** | Usabilidade | Tempo Percepção Status | < 10 seg | UX Feedback / Teste | Should |
| **RNF-06** | Confiabilidade | % Sucesso Jobs | > 98% | Dashboard de Saúde | Must |
| **RNF-07** | Confiabilidade | MTTR | < 2 horas | Incident Management | Should |
| **RNF-08** | Segurança | Vazamento de PII | Zero | Code/Log Scan | Must |
| **RNF-09** | Manutenibilidade | Cobertura de Testes | > 80% | CI/CD Reports | Should |
| **RNF-10** | Portabilidade | Tempo de Setup | < 30 min | Automação / IaC | Could |

---

## 5. Premissas e Limitações
1. **Infraestrutura:** Os SLOs de performance consideram uma instância mínima (ex: t3.medium). Upgrades de infra podem alterar esses valores.
2. **Qualidade da Origem:** A integridade de 100% pressupõe que o CSV de origem não possui erros estruturais intransponíveis.
3. **Rede:** A latência de dashboard assume conectividade estável entre Grafana e Postgres.
