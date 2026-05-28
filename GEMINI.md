# Olist SRE Pipeline - Decisões e Guia de Solução de Problemas

Este documento registra as lições aprendidas e as decisões técnicas tomadas durante a Aula 04 para garantir a reprodutibilidade do projeto.

## 🤖 Instruções para Agentes
Para diretrizes sobre o comportamento esperado, restrições da AWS Academy e padrões de documentação (RF-NN, RNF-NN), consulte:
- `documents/agents/GEMINI.md`

## 🧠 Decisões Arquiteturais (ADRs)

### ADR-01: Estabilidade de Dados (String vs JSON Experimental)
- **Problema:** O tipo `JSON` nativo do ClickHouse (experimental) causa erros `ILLEGAL_COLUMN (44)` ao realizar operações de `GROUP BY` ou `DISTINCT`.
- **Decisão:** Armazenar o objeto JSON como `String` na tabela `raw` e utilizar a função estável `JSONExtractString` nas Views analíticas.
- **Resultado:** Estabilidade garantida e compatibilidade com todas as versões recentes do ClickHouse.

### ADR-02: Resiliência de Inicialização (Wait-for-IT Nativo)
- **Problema:** Containers Python falhavam ao iniciar porque o ClickHouse ou MinIO demoravam alguns segundos a mais para aceitar conexões, mesmo após o status "healthy" do Docker.
- **Decisão:** Implementar um loop de *retry* (10 tentativas com intervalo de 5s) diretamente no código Python (`app/ingest_minio.py`).
- **Resultado:** Eliminação de crashes na inicialização (Race Conditions).

### ADR-03: Automação de Bootstrap
- **Problema:** Processo manual de upload de múltiplos CSVs via UI do MinIO era lento e propenso a erros.
- **Decisão:** Criar um script `app/upload_data.py` executado na inicialização do container `ingestor` para sincronizar a pasta local `./src/data` com o bucket `olist`.
- **Resultado:** Pipeline 100% automatizado "zero-touch" ao rodar `docker-compose up`.

## 🛠️ Guia de Solução de Problemas (Troubleshooting)

### 1. Erro de Autenticação no ClickHouse (Code 194)
- **Sintoma:** `Authentication failed: password is incorrect`.
- **Causa:** Conflito entre volumes antigos e nova senha configurada no `.env`.
- **Solução:** Limpar volumes e reiniciar: `docker-compose down -v && docker-compose up -d --build`.

### 2. View não encontrada no Dashboard (Code 60)
- **Sintoma:** `Unknown table expression identifier 'olist_raw.v_top_products'`.
- **Causa:** O ingestor falhou ao executar o script SQL da view ou ainda não terminou o processamento.
- **Validação:** Rodar `docker-compose logs -f ingestor` e verificar se a mensagem `SUCCESS: Initialized sql/views/01_top_products.sql` apareceu.

### 3. Dashboard Sem Dados
- **Sintoma:** Dashboard abre mas mostra "Nenhum dado processado".
- **Causa:** Arquivos `order_items` ou `products` não foram ingeridos corretamente.
- **Validação:** Verificar contagem no ClickHouse:
  `docker-compose exec clickhouse clickhouse-client --user default --password password123 --query "SELECT count() FROM olist_raw.ingestion"`

## 🚀 Como Replicar
1. Clone o repositório.
2. Certifique-se que os CSVs da Olist estão em `./data`.
3. Renomeie `.env.example` para `.env`.
4. Execute `docker-compose up -d --build`.
5. Aguarde ~1 minuto e acesse `localhost:8501`.
