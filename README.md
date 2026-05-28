# 20262sre-hermes-barboza
Repositorio para matéria de SRE da POS de eng de dados do Mackenzie.

## 🚀 Executando a Aula 04 (Pipeline Local)

Este projeto implementa um pipeline de dados resiliente e observável usando MinIO, ClickHouse e Streamlit.

### 1. Subir a Stack
Certifique-se de ter o Docker instalado e rode:
```bash
docker-compose up -d --build
```

### 2. Acessar os Serviços
- **MinIO Console:** [http://localhost:9003](http://localhost:9003) (user: `admin`, pass: `password123`)
- **ClickHouse HTTP:** [http://localhost:8123](http://localhost:8123)
- **Streamlit Dashboard:** [http://localhost:8501](http://localhost:8501)

### 3. Criar o Bucket e Carregar CSVs
1. Acesse o console do MinIO (localhost:9003).
2. Crie um bucket chamado `olist`.
3. Faça upload de qualquer arquivo CSV (ex: `olist_products_dataset.csv` da pasta `src/data/`).

### 4. Rodar o Ingestor
O container `ingestor` já está configurado para monitorar o bucket. Se você já subiu a stack, ele estará esperando pelos arquivos. Você pode ver os logs com:
```bash
docker-compose logs -f ingestor
```

### 5. Validar a View e o Dashboard
1. O ingestor carregará os dados para a tabela `raw` e a view `top_products`.
2. Acesse o dashboard no navegador [http://localhost:8501](http://localhost:8501) para ver as métricas e os dados ingeridos.

### 6. Idempotência
O sistema utiliza a coluna `unixtime` e `tag` (nome do arquivo) para garantir que apenas a versão mais recente de um arquivo seja exibida nas views analíticas, mesmo em caso de reprocessamento.
