# Plano de Testes de Carga — Olist SRE Pipeline

## 1. Introdução
Este documento detalha a estratégia de testes de performance para o pipeline de dados da Olist. O objetivo é validar se a arquitetura proposta (Python/EC2 + PostgreSQL) suporta o volume de dados alvo e se comporta de forma estável sob diferentes perfis de carga.

---

## 2. Cenários de Teste

### 2.1. Teste de Carga (Load Test)
- **Hipótese:** O sistema processa 100k registros dentro do SLO de 60 minutos sem degradação.
- **Ferramenta:** k6 (para simular requisições de ingestão ou disparos de jobs via API/CLI) + Scripts de geração de massa CSV.
- **Volume:** 100.000 registros (Carga Nominal Diária).
- **Duração:** Até a conclusão do processamento (estimado < 60 min).
- **Métrica de Sucesso:** Tempo total de execução < 60 min; Consumo de CPU/RAM estável na instância t3.medium.
- **RNF Coberto:** RNF-02 (Tempo de Processamento).

### 2.2. Teste de Estresse (Stress Test)
- **Hipótese:** Identificar o ponto de ruptura do sistema e como ele falha ao exceder a carga nominal.
- **Ferramenta:** k6 + Scripts de geração de massa CSV.
- **Volume:** Escalonamento gradual de 100k até 500k registros.
- **Duração:** 2 horas.
- **Métrica de Sucesso:** Identificação clara do gargalo (ex: I/O de disco no Postgres ou CPU no Python); O sistema não deve corromper dados ao falhar.
- **RNF Coberto:** RNF-06 (Confiabilidade), RNF-02 (Performance).

### 2.3. Teste de Pico (Spike Test)
- **Hipótese:** O sistema sobrevive a um aumento súbito e drástico no volume de arquivos de entrada (ex: Black Friday).
- **Ferramenta:** k6 (para injeção rápida de eventos).
- **Volume:** Disparo simultâneo de 5 lotes de 100k registros (Total 500k).
- **Duração:** 30 minutos de pico súbito.
- **Métrica de Sucesso:** O pipeline deve enfileirar ou processar sequencialmente sem queda da instância ou perda de conexão com o banco.
- **RNF Coberto:** RNF-06 (Confiabilidade), RNF-07 (Recuperação).

### 2.4. Teste de Resistência (Soak Test)
- **Hipótese:** O sistema mantém a performance e não apresenta vazamentos de memória ou exaustão de disco ao longo de múltiplas execuções.
- **Ferramenta:** k6 (agendador de execuções repetidas).
- **Volume:** 100k registros por execução, repetido por 24 horas.
- **Duração:** 24 horas.
- **Métrica de Sucesso:** Nenhuma tendência de aumento no consumo de memória base (memory leak); Limpeza de arquivos temporários funcionando corretamente.
- **RNF Coberto:** RNF-06 (Confiabilidade), RNF-09 (Manutenibilidade).

---

## 3. Relação com RNFs

| Cenário | RNF Principal | SLI Relacionado | SLO |
| :--- | :--- | :--- | :--- |
| **Load** | RNF-02 | Tempo total de execução | < 60 min |
| **Stress** | RNF-06 | % de Sucesso de Jobs | > 98% |
| **Spike** | RNF-07 | MTTR (Recuperação) | < 2 horas |
| **Soak** | RNF-09 | Estabilidade de Recursos | Sem Memory Leak |

---

## 4. Riscos e Ambiguidades

### Riscos
1. **Limitação de I/O (EBS):** Em instâncias t3.medium, o gargalo pode não ser CPU, mas a taxa de transferência do disco (EBS), afetando o SLO de 60 min.
2. **Custos de Outbound:** O volume de testes de carga pode gerar custos inesperados de transferência de dados se os arquivos não forem gerados localmente na VPC.
3. **Escopo do k6:** Como o k6 é focado em HTTP, sua aplicação direta em um script Python/SQL exige um "wrapper" (ex: API Flask local) para orquestrar os testes de carga de forma fidedigna.

### Ambiguidades
1. **Concorrência:** Não está claro se o pipeline deve suportar processamento paralelo de múltiplos arquivos ou se deve ser estritamente sequencial.
2. **Massa de Dados Realista:** O comportamento do Postgres (índices, vácuo) pode variar drasticamente entre dados sintéticos aleatórios e dados reais com distribuições específicas.
