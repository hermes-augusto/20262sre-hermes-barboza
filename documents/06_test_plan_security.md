# Plano de Testes de Segurança — Olist SRE Pipeline

## 1. Introdução
Este documento detalha o plano de testes de segurança para o pipeline de dados da Olist, utilizando metodologias reconhecidas como **STRIDE** e **OWASP Top 10** para identificar e mitigar ameaças na arquitetura proposta.

---

## 2. Análise de Ameaças (STRIDE)

| Componente | S (Spoofing) | T (Tampering) | R (Repudiation) | I (Info Disc.) | D (DoS) | E (Elevation) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Python ETL Script** | Identidade falsa ao conectar no S3/DB | Alteração maliciosa do código de transformação | Falha no registro de logs de execução | Exposição de credenciais em logs | Exaustão de recursos (CPU/RAM) | Execução de código com privilégios de root |
| **PostgreSQL** | Conexão de usuários não autorizados | Modificação direta de tabelas analíticas | Deleção de registros sem rastro | Acesso a dados de pedidos (PII) | Injeção de queries pesadas | Escalação de privilégios de usuário DB |
| **Grafana** | Sessão de usuário sequestrada | Alteração de dashboards por não autorizados | Falta de log de acesso ao dashboard | Visualização de dados por quem não deve | Sobrecarga de requisições ao portal | Acesso administrativo indevido |
| **S3 / Arquivos** | Upload de arquivo por origem falsa | Modificação do CSV bruto antes da carga | Falta de versão/audit do arquivo | Vazamento de dados via bucket público | Deletar arquivos brutos | Acesso via IAM mal configurado |

---

## 3. OWASP Top 10 Aplicáveis

1. **A01:2021-Broken Access Control:** Riscos de acesso indevido ao banco de dados e dashboards do Grafana.
2. **A03:2021-Injection:** Risco de SQL Injection nas transformações e Log Injection no monitoramento.
3. **A05:2021-Security Misconfiguration:** Configurações padrão de instâncias EC2, buckets S3 ou PostgreSQL expostos.
4. **A06:2021-Vulnerable and Outdated Components:** Uso de bibliotecas Python (Pandas/SQLAlchemy) com vulnerabilidades conhecidas.
5. **A09:2021-Security Logging and Monitoring Failures:** Falha em detectar atividades maliciosas no pipeline.

---

## 4. Casos de Teste de Segurança (TC-SEC)

| ID | Tipo | Ferramenta | Descrição | Componente |
| :--- | :--- | :--- | :--- | :--- |
| **TC-SEC-01** | SAST | Bandit | Analisar código Python em busca de vulnerabilidades comuns (ex: hardcoded keys, shell=True). | Python ETL |
| **TC-SEC-02** | SCA | Trivy | Verificar vulnerabilidades conhecidas (CVEs) em bibliotecas Python e imagens Docker. | Docker / Python |
| **TC-SEC-03** | DAST | OWASP ZAP | Escanear a interface web do Grafana em busca de falhas de segurança (XSS, CSRF). | Grafana |
| **TC-SEC-04** | Secret Scan | Gitleaks | Verificar se segredos, senhas ou AWS Keys foram commitados no repositório. | Código Fonte |
| **TC-SEC-05** | Cloud Posture | Prowler | Analisar a conformidade da infraestrutura AWS (S3, EC2, IAM) com as melhores práticas (CIS). | AWS Account |
| **TC-SEC-06** | DB Security | Sqlmap | Tentar injeção de SQL simulada em parâmetros de entrada do pipeline. | PostgreSQL |

---

## 5. Riscos e Ambiguidades

### Riscos
1. **Privilégios Excessivos (IAM):** No ambiente AWS Academy, há pouco controle sobre as Roles, o que pode levar a permissões maiores que o necessário (*Least Privilege* violado).
2. **Dados Sensíveis (PII):** O pipeline lida com pedidos; se houver vazamento de logs com nomes/CPFs, o sistema violará a LGPD (RNF-08).
3. **Persistência de Segredos:** A falta de um Secrets Manager (devido a restrições de custo/academy) pode levar ao armazenamento de senhas em variáveis de ambiente inseguras.

### Ambiguidades
1. **Autenticação de Ingestão:** Não está definido se a ingestão valida a assinatura digital dos arquivos CSV para evitar *Spoofing*.
2. **Isolamento de Rede:** Não está claro se o banco de dados estará em uma sub-rede privada, limitando o vetor de ataque externo.
