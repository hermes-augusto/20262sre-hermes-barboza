# Matriz de Rastreabilidade de Requisitos (RTM) — Olist SRE Pipeline

## 1. Introdução
Este documento rastreia cada requisito (Funcional e Não Funcional) desde sua origem até o componente arquitetural e o caso de teste correspondente, garantindo cobertura total do sistema.

---

## 2. Matriz de Rastreabilidade

| Req | Tipo | Origem | Componente | Caso de teste | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **RF-01** | Funcional | spec/00_problem.md | Python ETL Script (Injestor) | TC-01: Ingestão de CSV Válido | Coberto |
| **RF-02** | Funcional | spec/00_problem.md | PostgreSQL (Silver/Stage) | TC-02: Carga na Camada Stage | Coberto |
| **RF-03** | Funcional | spec/00_problem.md | PostgreSQL (Gold/Analítico) | TC-03: Transformação Analítica | Coberto |
| **RF-04** | Funcional | spec/00_problem.md | PostgreSQL / Python ETL | TC-04: Teste de Idempotência | Coberto |
| **RF-05** | Funcional | spec/00_problem.md | Grafana Dashboard | TC-05: Visualização de Dados | Coberto |
| **RF-06** | Funcional | spec/00_problem.md | Python ETL Script (Erro) | TC-06: Arquivo Corrompido | Coberto |
| **RF-07** | Funcional | spec/00_problem.md | CloudWatch / Grafana | TC-07: Emissão de Métricas | Coberto |
| **RF-08** | Funcional | spec/00_problem.md | Docker / IaC | - | **Aberto** |
| **RNF-01** | Não Funcional | ISO 25010 | PostgreSQL / Python ETL | TC-08: Conciliação de Registros | Coberto |
| **RNF-02** | Não Funcional | ISO 25010 | Python ETL / EC2 | TC-09: Stress Test 100k reg. | Coberto |
| **RNF-03** | Não Funcional | ISO 25010 | Grafana / PostgreSQL | TC-10: Latência Fim-a-Fim | Coberto |
| **RNF-04** | Não Funcional | ISO 25010 | PostgreSQL | TC-11: Verificação de Versão | Coberto |
| **RNF-05** | Não Funcional | ISO 25010 | Grafana Dashboard | - | **Aberto** |
| **RNF-06** | Não Funcional | ISO 25010 | CloudWatch / Grafana | TC-12: Histórico de Sucesso | Coberto |
| **RNF-07** | Não Funcional | ISO 25010 | Docker / IaC | - | **Aberto** |
| **RNF-08** | Não Funcional | ISO 25010 | Python ETL / CloudWatch | TC-13: Scan de PII em Logs | Coberto |
| **RNF-09** | Não Funcional | ISO 25010 | CI/CD / Pytest | TC-14: Relatório de Cobertura | Coberto |
| **RNF-10** | Não Funcional | ISO 25010 | Docker / IaC | TC-15: Fresh Deploy Time | Coberto |

---

## 3. Sumário de Cobertura

- **Total de Requisitos:** 18
- **Requisitos Cobertos:** 15
- **Requisitos Abertos:** 3
  - **RF-08:** Falta detalhar o caso de teste para resiliência a quedas de instância.
  - **RNF-05:** Falta definir como medir objetivamente o "Tempo de Percepção do Status".
  - **RNF-07:** Falta detalhar o caso de teste para MTTR de infraestrutura.

---

## 4. Riscos e Ambiguidades

### Riscos
1. **Ambiente de Teste (RF-08):** Simular uma queda de instância EC2 no AWS Academy pode ser complexo sem permissões avançadas.
2. **Volumetria (RNF-02):** A instância t3.medium pode não sustentar o SLO de 60 minutos se a lógica de transformação for ineficiente.
3. **Persistência de Logs (RNF-08):** Logs de erro detalhados podem acidentalmente capturar dados se não houver um middleware de higienização.

### Ambiguidades
1. **Definição de "Status Claro" (RNF-05):** O que é "claro" para um stakeholder pode não ser para outro; requer validação de UX.
2. **Fonte de Verdade (RNF-01):** Em caso de falha na ingestão, como o sistema garantirá que a contagem do CSV de origem é a "verdade absoluta"?
