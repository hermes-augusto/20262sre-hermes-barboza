## Quando usar
Quando o usuario pedir RNFs e ja existir spec/00_problem.md
e/ou documents/01_functional_requirements.md.

## Entrada
- spec/00_problem.md (obrigatorio)
- documents/01_functional_requirements.md (opcional)

## Passos
1. Ler stakeholders e fluxos criticos do problema.
2. Mapear cada fluxo aos 8 atributos da ISO 25010.
3. Para cada atributo, propor 1 a 3 RNFs com SLI mensuravel.
4. Marcar prioridade MoSCoW.
5. Listar premissas e fontes de medicao.

## Saida
Arquivo documents/02_non_functional_requirements.md com:
- secao por atributo ISO 25010
- IDs RNF-NN unicos
- tabela final com (ID, atributo, SLI, SLO, fonte, prioridade)

## Criterios de aceitacao
- 8 atributos cobertos.
- Todo RNF tem unidade e janela.
- Nenhum RNF aspiracional ("ser confiavel" e proibido).