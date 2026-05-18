# Problema — Olist SRE Pipeline

## Contexto
Marketplace Olist precisa de ETL diário confiavel para ~100k pedidos.

## Stakeholders
- Operação Olist (negócio)
- Time de dados
- Consumidores dos dashboards
- Plataforma / SRE

## Fluxos críticos
1. Ingestão CSV -> transformação -> Postgres
2. Atualização de dashboards Grafana
3. Observação contínua de SLA

## Modos de falha conhecidos
- Arquivo parcial / corrompido
- Reprocesso duplicando linhas
- EC2 derrubada durante run
- Banco indisponível
