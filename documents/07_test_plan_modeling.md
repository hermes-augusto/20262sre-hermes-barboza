# Plano de Testes de Modelagem (ATAM e Caos) — Olist SRE Pipeline

## 1. Introdução
Este documento descreve o plano de testes de modelagem para o pipeline de dados da Olist, utilizando o método **ATAM (Architecture Tradeoff Analysis Method)** para avaliar decisões arquiteturais e **Engenharia de Caos** para validar a resiliência do sistema sob condições adversas.

O foco é garantir que os atributos de qualidade (RNFs) definidos sejam atendidos pelas decisões tomadas na arquitetura (RM-ODP e ADRs).

---

## 2. Análise ATAM (Architecture Tradeoff Analysis Method)

### 2.1. Utility Tree
A Utility Tree prioriza os atributos de qualidade e os desdobra em cenários de teste, identificando Riscos, Pontos de Sensibilidade e Trade-offs.

| Atributo de Qualidade | Cenário (Estímulo -> Resposta) | Sensibilidade | Trade-off | Risco |
| :--- | :--- | :--- | :--- | :--- |
| **Performance (RNF-02)** | Ingestão de 100k pedidos em < 60 min na t3.medium. | Alta: Depende de índices no Postgres e CPU da EC2. | **T01:** Simplicidade (Python) vs. Escalabilidade Gerenciada (Glue). | Médio: Volume de dados crescer além da capacidade da instância única. |
| **Confiabilidade (RNF-06)** | Falha no meio da carga deve ser recuperada sem duplicidade (Idempotência). | Alta: Estratégia de Truncate-Load na camada Stage. | **T02:** Rapidez de Carga vs. Garantia de Estado (Limpeza prévia). | Baixo: Se o `TRUNCATE` falhar, o estado fica inconsistente. |
| **Segurança (RNF-08)** | Erro crítico no ETL não deve expor PII nos logs do CloudWatch. | Média: Regex de higienização nos logs. | **T03:** Detalhamento do Erro vs. Proteção de Dados. | Alto: Logs detalhados são úteis para SRE mas perigosos para LGPD. |
| **Operabilidade (RNF-05)** | Dashboard deve mostrar falha em < 10s após o erro. | Baixa: Frequência de refresh do Grafana. | - | Baixo: Latência de rede entre DB e Grafana. |

### 2.2. Avaliação de Trade-offs e Sensibilidades
- **[T01] Trade-off Performance/Custo:** A decisão de usar EC2 + Python (ADR-01) economiza custos no AWS Academy, mas transfere o risco de performance para a gestão manual de recursos (SRE).
- **[T02] Sensibilidade de Integridade:** A idempotência baseada em `TRUNCATE` (ADR-03) é sensível à disponibilidade do banco. Se o banco cair durante a limpeza, o reprocessamento pode falhar ou duplicar dados.
- **[Ponto de Sensibilidade] Camada Analítica:** O uso de PostgreSQL como DW (ADR-02) exige manutenção constante de `VACUUM` e índices para manter o RNF-02 conforme o volume histórico cresce.

---

## 3. Testes de Engenharia de Caos (Chaos Engineering)

Os testes de caos validam o comportamento do sistema em situações "indesejadas" (RF-06 e RF-08).

### TC-CHAOS-01: Falha Súbita do Runner (EC2)
- **Hipótese:** Se o processo Python for interrompido (`kill -9`) durante a transformação analítica, a próxima execução deve limpar o estado parcial e completar o processamento sem duplicar registros na camada Gold.
- **Método:** Abortar o script no meio da execução. Reiniciar e verificar contagem final de registros.
- **Métrica de Sucesso:** Integridade = 100% (RNF-01).

### TC-CHAOS-02: Indisponibilidade de Banco de Dados
- **Hipótese:** Se a conexão com o PostgreSQL cair durante a ingestão, o sistema deve logar o erro de conexão e encerrar de forma limpa, permitindo MTTR < 2h (RNF-07).
- **Método:** Bloquear porta 5432 via Security Group durante a execução.
- **Métrica de Sucesso:** Presença de logs de erro claros (RNF-05) e encerramento controlado (sem "zombie processes").

### TC-CHAOS-03: Exaustão de Recursos (Disco/Memory)
- **Hipótese:** Se o diretório de logs ou stage temporário encher, o sistema deve interromper a execução para evitar corrupção de arquivos CSV.
- **Método:** Preencher o disco da EC2 (`dd if=/dev/zero...`) antes do início do job.
- **Métrica de Sucesso:** Interrupção segura (RF-06) e alerta de monitoramento emitido (RF-07).

---

## 4. Casos de Teste de Modelagem (Resiliência)

| ID | Descrição | Requisito Alvo | Critério de Aceitação |
| :--- | :--- | :--- | :--- |
| **TC-16** | Validação de Idempotência (Double Run) | RF-04 | Executar o mesmo lote 2x; a contagem final no banco deve ser idêntica a 1x. |
| **TC-17** | Recuperação MTTR (Manual Override) | RNF-07 | Simular falha e cronometrar tempo de subida de novo runner via Docker (Alvo < 30 min). |
| **TC-18** | Verificação de Scan LGPD | RNF-08 | Inserir dado falso sensível (CPF) no CSV e validar se o pipeline o remove/mascara antes da carga. |

---

## 5. Riscos e Ambiguidades

### Riscos
1. **Sobrecarga do PostgreSQL (ADR-02):** Como o banco atua como Stage e Analítico, queries pesadas do Grafana podem impactar o tempo de carga (RNF-02).
2. **Falsos Positivos em Idempotência:** A estratégia de `TRUNCATE` pode mascarar falhas de lógica se não houver uma auditoria de "total de registros esperados" vindo do CSV.
3. **Limitações do AWS Academy:** A falta de instâncias multi-AZ pode invalidar o teste de resiliência de infraestrutura real, limitando-nos a testes de processo/software.

### Ambiguidades
1. **Definição de "Estado Íntegro" (RF-08):** Não está claro se o sistema deve reverter para o estado anterior à falha ou apenas limpar o que foi tentado na execução atual.
2. **Granularidade das Métricas (RF-07):** O tempo de execução deve ser medido por "etapa" ou "total"? A ambiguidade pode afetar a análise de gargalos (Performance).
