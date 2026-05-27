# skills/elicit_rf.md

## Quando usar
Quando o usuario pedir Requisitos Funcionais (RF) e ja existir spec/00_problem.md.

## Entrada
- specs/00_problem.md (obrigatorio)

## Passos
1. Ler o contexto do problema, fluxos criticos e stakeholders.
2. Identificar cada acao do sistema como um RF.
3. Aplicar a sintaxe EARS (Ubiquo, Estado, Evento, Opcional, Indesejado).
4. Definir criterios de aceitacao em Gherkin (Given/When/Then).
5. Atribuir prioridade MoSCoW (Must, Should, Could, Won't).

## Saida
Arquivo documents/01_functional_requirements.md com:
- Anatomia completa: ID (RF-NN), Titulo, Descricao EARS, Atores, Pre/Pos-condicoes, Gherkin.
- Tabela resumo com ID, RF, Ator e Prioridade.
- Riscos e ambiguidades.