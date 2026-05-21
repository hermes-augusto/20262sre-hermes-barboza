# skills/build_rtm.md

## Quando usar
Quando o usuario pedir a Matrix de Rastreabilidade (RTM) e ja existirem os documentos de requisitos e arquitetura.

## Entrada
- documents/01_functional_requirements.md
- documents/02_non_functional_requirements.md
- documents/03_architecture.md

## Passos
1. Coletar todos os IDs de RF e RNF.
2. Identificar a origem de cada requisito (Stakeholder ou Documento).
3. Mapear cada requisito ao componente de arquitetura correspondente (do RM-ODP).
4. Propor IDs de casos de teste (TC-NN) para cada requisito.
5. Identificar requisitos sem cobertura (Gaps).

## Saida
Arquivo documents/04_rtm.md como tabela markdown com:
- Colunas: Req | Tipo | Origem | Componente | Caso de teste | Status.
- Contagem final de requisitos abertos vs. cobertos.
- 3 riscos e 2 ambiguidades.