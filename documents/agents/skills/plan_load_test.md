# skills/plan_load_test.md

## Quando usar
Quando o usuario pedir o plano de testes de carga baseado na arquitetura e RNFs.

## Entrada
- documents/03_architecture.md
- documents/02_non_functional_requirements.md

## Passos
1. Identificar cenários críticos de performance.
2. Definir 4 tipos de testes: Load, Soak, Spike, Stress.
3. Para cada cenário, definir: hipótese, ferramenta (k6), volume, duração, métrica de sucesso e RNF coberto.

## Saida
Arquivo documents/05_test_plan_load.md com:
- Detalhamento dos 4 cenários.
- Relação com RNFs.
- 3 riscos e 2 ambiguidades.