# skills/plan_modeling_test.md

## Quando usar
Quando o usuario pedir o plano de testes de modelagem (ATAM/Chaos).

## Entrada
- documents/03_architecture.md
- documents/02_non_functional_requirements.md

## Passos
1. Realizar um ATAM (Architecture Tradeoff Analysis Method) reduzido.
2. Usar cenários da utility tree para classificar como risco/sensibilidade/trade-off.
3. Incluir testes de caos (TC-CHAOS-NN) para cada closed loop (backpressure, circuit breaker, etc).

## Saida
Arquivo documents/07_test_plan_modeling.md com:
- Análise ATAM.
- Casos de teste de caos.
- 3 riscos e 2 ambiguidades.