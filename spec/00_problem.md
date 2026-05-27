# Problema — Olist SRE Pipeline

## 1. Contexto
O negócio Olist precisa processar aproximadamente 100 mil pedidos do marketplace diariamente, carregá-los em um banco analítico e gerar dashboards de suporte à decisão. O sistema deve ser um pilar de confiança para a operação, garantindo que o ETL seja confiável, resiliente e transparente.

## 2. Stakeholders
- **Operação Olist (Negócio):** Depende dos números para tomada de decisão estratégica.
- **Time de Dados:** Responsável pela qualidade, modelagem e integridade das informações.
- **Consumidores dos Dashboards:** Usuários finais que visualizam os dados para acompanhamento diário.
- **Time de Plataforma / SRE:** Garante a estabilidade, escalabilidade, observabilidade e automação do pipeline.

## 3. Fluxos Críticos
1. **Ingestão e Carga:** Captura de arquivos CSV brutos e carga inicial no Postgres.
2. **Transformação Analítica:** Processamento dos dados para o formato de consumo.
3. **Atualização de Dashboards:** Disponibilização dos dados processados no Grafana.
4. **Observação de SLA:** Monitoramento contínuo da saúde, pontualidade e integridade do pipeline.

## 4. Modos de Falha Conhecidos
- **Arquivo parcial / corrompido:** Ingestão de dados truncados ou inválidos.
- **Reprocessamento com duplicidade:** Falta de idempotência gerando inflação nos indicadores.
- **Interrupção de Infraestrutura (EC2):** Queda da instância durante o processamento (falha no meio da run).
- **Indisponibilidade de Banco de Dados:** Falha na persistência final dos dados processados.
- **Falha Silenciosa:** O pipeline termina sem erros aparentes, mas com dados ausentes ou incorretos.

## 5. Propriedades Emergentes Alvo
- **Idempotência:** O sistema deve produzir o mesmo resultado final, independente de quantas vezes o processo for repetido para o mesmo período.
- **Observabilidade:** Telemetria clara (logs, métricas, traces) para identificar gargalos e falhas rapidamente.
- **Resiliência:** Capacidade de se recuperar ou mitigar falhas parciais sem perda de dados.
- **Confiabilidade (Trust):** Garantia de que o dado no dashboard reflete a realidade da ingestão.

## 6. Fora de Escopo
- Otimizações avançadas de custo de cloud (nesta fase inicial).
- Governança de dados profunda (catálogos de dados, linhagem complexa).
- Segurança de rede granular (IAM Roles complexas, VPC Peering).

## 7. Pergunta Orientadora
> **O que o sistema precisa garantir para que o negócio confie nos números do dashboard?**
