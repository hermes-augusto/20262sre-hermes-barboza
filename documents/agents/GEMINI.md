# AGENTS.md · olist-sre-pipeline

## Contexto
Pipeline de dados Olist em AWS Academy Learner Lab (us-east-1).
ETL Python -> Postgres -> Grafana. SRE-first.

## Restrições duras
- Sem Glue, Redshift, SageMaker (Learner Lab nao habilita).
- Sem secrets em codigo. Tudo via SSM Parameter Store.
- Sem provisionar nada nesta aula. Apenas markdown e Mermaid.

## Saida esperada
- Markdown valido com cabecalhos hierarquicos.
- IDs estaveis: RF-NN, RNF-NN, TC-NN, ADR-NN.
- RNF mensuravel: valor, unidade, janela, fonte.
- Premissas e questoes em aberto ao final.

## Comportamento
- Critique sua saida antes de entregar.
- Liste 3 riscos e 2 ambiguidades por arquivo.
- Use as skills em documents/agents/skills/.
- Nao invente nomes de servico AWS.