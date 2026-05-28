-- View v_top_products: Consolida dados de itens, produtos e traduções para análise de receita
-- Usamos JSONExtractString para garantir tipagem String estável para o GROUP BY

CREATE OR REPLACE VIEW olist_raw.v_top_products AS
WITH 
-- Identifica o timestamp da última ingestão para cada arquivo
latest_ingestion AS (
    SELECT 
        tag, 
        max(unixtime) as max_ts
    FROM olist_raw.ingestion
    GROUP BY tag
),

-- Extrai itens de pedidos (contém preços e IDs de produto)
items AS (
    SELECT 
        JSONExtractString(data, 'product_id') AS product_id,
        JSONExtractString(data, 'order_id') AS order_id,
        toDecimal64(JSONExtractString(data, 'price'), 2) AS price
    FROM olist_raw.ingestion
    INNER JOIN latest_ingestion 
        ON olist_raw.ingestion.tag = latest_ingestion.tag 
        AND olist_raw.ingestion.unixtime = latest_ingestion.max_ts
    WHERE olist_raw.ingestion.tag LIKE '%order_items%'
),

-- Extrai metadados de produtos (contém categorias)
products AS (
    SELECT 
        JSONExtractString(data, 'product_id') AS product_id,
        JSONExtractString(data, 'product_category_name') AS product_category_name
    FROM olist_raw.ingestion
    INNER JOIN latest_ingestion 
        ON olist_raw.ingestion.tag = latest_ingestion.tag 
        AND olist_raw.ingestion.unixtime = latest_ingestion.max_ts
    WHERE olist_raw.ingestion.tag LIKE '%products_dataset%'
),

-- Extrai tradução das categorias
translations AS (
    SELECT 
        JSONExtractString(data, 'product_category_name') AS product_category_name,
        JSONExtractString(data, 'product_category_name_english') AS product_category_name_english
    FROM olist_raw.ingestion
    INNER JOIN latest_ingestion 
        ON olist_raw.ingestion.tag = latest_ingestion.tag 
        AND olist_raw.ingestion.unixtime = latest_ingestion.max_ts
    WHERE olist_raw.ingestion.tag LIKE '%category_name_translation%'
)

-- Agregação final para o ranking de receita
SELECT 
    p.product_id AS product_id,
    p.product_category_name AS product_category_name,
    t.product_category_name_english AS product_category_name_english,
    count(DISTINCT i.order_id) AS total_orders,
    count() AS total_items,
    sum(i.price) AS revenue
FROM items i
LEFT JOIN products p ON i.product_id = p.product_id
LEFT JOIN translations t ON p.product_category_name = t.product_category_name
GROUP BY 
    product_id, 
    product_category_name, 
    product_category_name_english
ORDER BY revenue DESC;
