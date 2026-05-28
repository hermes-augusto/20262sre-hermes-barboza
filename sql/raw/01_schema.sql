CREATE DATABASE IF NOT EXISTS olist_raw;

CREATE TABLE IF NOT EXISTS olist_raw.ingestion (
    unixtime Int64,
    data String,
    tag LowCardinality(String)
) ENGINE = MergeTree()
ORDER BY (tag, unixtime);
