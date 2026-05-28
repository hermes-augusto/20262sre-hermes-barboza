# Runbook: Setup e Execucao do Pipeline Olist na AWS

Este documento descreve todos os passos necessarios para subir o pipeline completo localmente com conexao ao S3 da AWS.

---

## 1. Pre-requisitos

- Docker e Docker Compose instalados
- Acesso as credenciais AWS Student Lab
- Arquivos do repositorio

---

## 2. Configuracao das Credenciais AWS

Criar/atualizar o arquivo `.env` na raiz do projeto:

```bash
AWS_ACCESS_KEY_ID=<ACCESS_KEY>
AWS_SECRET_ACCESS_KEY=<SECRET_KEY>
AWS_SESSION_TOKEN=<SESSION_TOKEN>
S3_BUCKET_NAME=olist-data-601804900997-us-east-1
AWS_REGION=us-east-1
```

**Nota:** O nome do bucket e `olist-data-601804900997-us-east-1`, NAO `olist`.

Verificar se `.env` esta no `.gitignore` para evitar commit de credenciais.

---

## 3. Arquivos Necessarios

### 3.1 Dockerfile (na raiz)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ .
CMD ["tail", "-f", "/dev/null"]
```

### 3.2 docker-compose.aws.yaml

O arquivo deve conter:
- **clickhouse**: Banco analitico (portas 8123, 9000)
- **dashboard**: Streamlit (porta 8501)
- **ingestor**: Worker para ingestao do S3

Variaveis de ambiente obrigatorias no ingestor:
```yaml
environment:
  - CLICKHOUSE_HOST=clickhouse
  - CLICKHOUSE_PORT=8123
  - CLICKHOUSE_USER=ingest
  - CLICKHOUSE_PASSWORD=ingest
  - S3_BUCKET_NAME=${S3_BUCKET_NAME}
  - AWS_REGION=${AWS_REGION}
  - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
  - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
  - AWS_SESSION_TOKEN=${AWS_SESSION_TOKEN}
```

### 3.3 Diretorio app/

```
app/
  requirements.txt    # streamlit, clickhouse-connect, boto3, pandas
  streamlit_app.py    # Dashboard
  ingest.py           # Script de ingestao S3 -> ClickHouse
```

---

## 4. Subir os Containers

```bash
docker compose -f docker-compose.aws.yaml up -d --build
```

Verificar status:
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

Todos os containers devem estar `Up` e o clickhouse `Healthy`.

---

## 5. Criar Usuarios e Banco no ClickHouse

O ClickHouse so vem com o usuario `default`. Criar os usuarios necessarios:

```bash
# Criar usuarios
docker exec olist_analytics clickhouse-client --query "CREATE USER IF NOT EXISTS dashboard IDENTIFIED BY 'dashboard'"
docker exec olist_analytics clickhouse-client --query "CREATE USER IF NOT EXISTS ingest IDENTIFIED BY 'ingest'"

# Criar banco
docker exec olist_analytics clickhouse-client --query "CREATE DATABASE IF NOT EXISTS olist"

# Conceder permissoes
docker exec olist_analytics clickhouse-client --query "GRANT ALL ON olist.* TO dashboard"
docker exec olist_analytics clickhouse-client --query "GRANT ALL ON olist.* TO ingest"
```

---

## 6. Ingerir Dados do S3

Executar o script de ingestao:

```bash
docker exec olist_ingestor python ingest.py
```

Tabelas que serao criadas:
- `olist.orders` (~99k registros)
- `olist.order_items` (~112k registros)
- `olist.order_payments` (~103k registros)
- `olist.order_reviews` (~82k registros)
- `olist.customers` (~99k registros)
- `olist.geolocation` (~1M registros)
- `olist.products` (~32k registros)
- `olist.sellers` (~3k registros)

---

## 7. Acessar os Servicos

| Servico | URL |
|---------|-----|
| Dashboard | http://localhost:8501 |
| ClickHouse HTTP | http://localhost:8123 |
| ClickHouse Native | localhost:9000 |

---

## 8. Problemas Comuns e Solucoes

### 8.1 Erro "Authentication failed" no Dashboard

**Causa:** Usuarios `dashboard` ou `ingest` nao criados no ClickHouse.

**Solucao:** Executar os comandos da secao 5.

### 8.2 Erro "Unable to locate credentials" no Ingestor

**Causa:** Variaveis AWS nao passadas para o container.

**Solucao:** Verificar se `docker-compose.aws.yaml` tem todas as variaveis AWS no servico `ingestor` e se o `.env` esta preenchido.

### 8.3 Erro "Access Denied" no S3

**Causa:** Bucket name incorreto ou credenciais sem permissao.

**Solucao:** Verificar o nome do bucket com:
```bash
docker exec olist_ingestor python -c "
import boto3, os
s3 = boto3.client('s3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
    region_name=os.getenv('AWS_REGION', 'us-east-1'))
for b in s3.list_buckets()['Buckets']:
    print(b['Name'])
"
```

### 8.4 Erro "Unrecognized column" na Ingestao

**Causa:** CSV com aspas nos nomes das colunas.

**Solucao:** O `ingest.py` deve fazer `.strip('"')` nos headers e valores.

### 8.5 Dashboard sem dados

**Causa:** Ingestao nao executada ou com erro.

**Solucao:** Verificar tabelas:
```bash
docker exec olist_analytics clickhouse-client --query "SELECT name, total_rows FROM system.tables WHERE database='olist'"
```

---

## 9. Comandos Uteis

```bash
# Logs dos containers
docker logs olist_dashboard
docker logs olist_ingestor
docker logs olist_analytics

# Acessar ClickHouse client
docker exec -it olist_analytics clickhouse-client

# Listar tabelas
docker exec olist_analytics clickhouse-client --query "SHOW TABLES FROM olist"

# Contar registros
docker exec olist_analytics clickhouse-client --query "SELECT count() FROM olist.orders"

# Reiniciar container
docker compose -f docker-compose.aws.yaml restart <servico>

# Parar tudo
docker compose -f docker-compose.aws.yaml down

# Limpar volumes
docker compose -f docker-compose.aws.yaml down -v
```

---

## 10. Arquitetura

```
S3 (AWS) --> Ingestor (Python) --> ClickHouse --> Dashboard (Streamlit)
                         |
                    boto3 + credentials
```

- **S3**: Bucket `olist-data-601804900997-us-east-1` com CSVs
- **Ingestor**: Python com boto3, le CSV do S3 e insere no ClickHouse
- **ClickHouse**: Banco analitico, dados na tabela `olist.*`
- **Dashboard**: Streamlit com metricas, graficos e explorador de dados
