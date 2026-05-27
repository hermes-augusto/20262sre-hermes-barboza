# skills/plan_security_test.md

## Quando usar
Quando o usuario pedir o plano de testes de segurança baseado na arquitetura.

## Entrada
- documents/03_architecture.md

## Passos
1. Aplicar o modelo STRIDE em cada componente da arquitetura.
2. Identificar riscos baseados no OWASP Top 10 aplicáveis.
3. Definir casos de teste (TC-SEC-NN) para: SAST (Bandit), SCA (Trivy), DAST (ZAP), secret scan (gitleaks) e cloud posture (Prowler).

## Saida
Arquivo documents/06_test_plan_security.md com:
- Análise STRIDE por componente.
- Tabela de casos de teste de segurança.
- 3 riscos e 2 ambiguidades.