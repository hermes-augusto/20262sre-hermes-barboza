import streamlit as st
import clickhouse_connect
import pandas as pd
import os

st.set_page_config(page_title="Olist Analytics Dashboard", layout="wide")

st.title("Olist Analytics Dashboard")


@st.cache_resource
def get_client():
    return clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST", "clickhouse"),
        port=int(os.getenv("CLICKHOUSE_PORT", "8123")),
        username=os.getenv("CLICKHOUSE_USER", "dashboard"),
        password=os.getenv("CLICKHOUSE_PASSWORD", "dashboard"),
    )


client = get_client()

try:
    client.ping()
except Exception as e:
    st.error(f"Erro de conexão: {e}")
    st.stop()

# ============================================================
# KPIs
# ============================================================
st.header("Metricas Gerais")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_orders = client.query("SELECT count() FROM olist.orders").result_rows[0][0]
    st.metric("Total de Pedidos", f"{total_orders:,}")

with col2:
    total_revenue = client.query(
        "SELECT round(sum(CAST(payment_value AS Float64)), 2) FROM olist.order_payments"
    ).result_rows[0][0]
    st.metric("Receita Total", f"R$ {total_revenue:,.2f}")

with col3:
    avg_order = client.query(
        "SELECT round(avg(CAST(payment_value AS Float64)), 2) FROM olist.order_payments"
    ).result_rows[0][0]
    st.metric("Ticket Medio", f"R$ {avg_order:,.2f}")

with col4:
    total_customers = client.query("SELECT count() FROM olist.customers").result_rows[0][0]
    st.metric("Total Clientes", f"{total_customers:,}")

with col5:
    total_sellers = client.query("SELECT count() FROM olist.sellers").result_rows[0][0]
    st.metric("Total Vendedores", f"{total_sellers:,}")

st.divider()

# ============================================================
# Pedidos por Mes (Linha)
# ============================================================
st.header("Tendencia de Pedidos por Mes")

df_orders_monthly = client.query_df("""
    SELECT
        substring(order_purchase_timestamp, 1, 7) AS mes,
        count() AS total_pedidos
    FROM olist.orders
    GROUP BY mes
    ORDER BY mes
""")

if not df_orders_monthly.empty:
    df_orders_monthly.columns = ["Mes", "Total Pedidos"]
    st.line_chart(df_orders_monthly.set_index("Mes"))

st.divider()

# ============================================================
# Receita por Categoria (Barras)
# ============================================================
st.header("Receita por Categoria do Produto")

df_revenue_category = client.query_df("""
    SELECT
        t2.product_category_name AS categoria,
        round(sum(CAST(t3.payment_value AS Float64)), 2) AS receita
    FROM olist.order_items t1
    JOIN olist.products t2 ON t1.product_id = t2.product_id
    JOIN olist.order_payments t3 ON t1.order_id = t3.order_id
    WHERE t2.product_category_name != ''
    GROUP BY categoria
    ORDER BY receita DESC
    LIMIT 15
""")

if not df_revenue_category.empty:
    df_revenue_category.columns = ["Categoria", "Receita"]
    st.bar_chart(df_revenue_category.set_index("Categoria"))

st.divider()

# ============================================================
# Status dos Pedidos (Pie)
# ============================================================
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Distribuicao por Status do Pedido")

    df_order_status = client.query_df("""
        SELECT
            order_status AS status,
            count() AS total
        FROM olist.orders
        GROUP BY status
        ORDER BY total DESC
    """)

    if not df_order_status.empty:
        df_order_status.columns = ["Status", "Total"]
        st.bar_chart(df_order_status.set_index("Status"))

with col_right:
    st.subheader("Tipos de Pagamento")

    df_payment_type = client.query_df("""
        SELECT
            payment_type AS tipo,
            count() AS total
        FROM olist.order_payments
        GROUP BY tipo
        ORDER BY total DESC
    """)

    if not df_payment_type.empty:
        df_payment_type.columns = ["Tipo", "Total"]
        st.bar_chart(df_payment_type.set_index("Tipo"))

st.divider()

# ============================================================
# Top 10 Vendedores
# ============================================================
st.header("Top 10 Vendedores por Numero de Pedidos")

df_top_sellers = client.query_df("""
    SELECT
        t1.seller_id AS vendedor,
        count(DISTINCT t1.order_id) AS total_pedidos,
        round(sum(CAST(t3.payment_value AS Float64)), 2) AS receita_total
    FROM olist.order_items t1
    JOIN olist.order_payments t3 ON t1.order_id = t3.order_id
    GROUP BY vendedor
    ORDER BY total_pedidos DESC
    LIMIT 10
""")

if not df_top_sellers.empty:
    df_top_sellers.columns = ["Vendedor", "Total Pedidos", "Receita Total"]
    st.dataframe(df_top_sellers, use_container_width=True)

st.divider()

# ============================================================
# Clientes por Estado
# ============================================================
st.header("Distribuicao de Clientes por Estado")

df_customers_state = client.query_df("""
    SELECT
        customer_state AS estado,
        count() AS total
    FROM olist.customers
    GROUP BY estado
    ORDER BY total DESC
""")

if not df_customers_state.empty:
    df_customers_state.columns = ["Estado", "Total"]
    st.bar_chart(df_customers_state.set_index("Estado"))

st.divider()

# ============================================================
# Notas de Avaliacao
# ============================================================
col_left2, col_right2 = st.columns(2)

with col_left2:
    st.subheader("Distribuicao de Notas de Avaliacao")

    df_review_scores = client.query_df("""
        SELECT
            review_score AS nota,
            count() AS total
        FROM olist.order_reviews
        GROUP BY nota
        ORDER BY nota
    """)

    if not df_review_scores.empty:
        df_review_scores.columns = ["Nota", "Total"]
        st.bar_chart(df_review_scores.set_index("Nota"))

with col_right2:
    st.subheader("Tempo Medio de Entrega por Estado (dias)")

    df_delivery_time = client.query_df("""
        SELECT
            t1.customer_state AS estado,
            round(avg(dateDiff('day',
                toDateTime(t2.order_purchase_timestamp),
                toDateTime(t2.order_delivered_customer_date)
            )), 1) AS dias_medios
        FROM olist.customers t1
        JOIN olist.orders t2 ON t1.customer_id = t2.customer_id
        WHERE t2.order_delivered_customer_date != '0000-00-00 00:00:00'
          AND t2.order_delivered_customer_date != ''
        GROUP BY estado
        ORDER BY dias_medios DESC
        LIMIT 15
    """)

    if not df_delivery_time.empty:
        df_delivery_time.columns = ["Estado", "Dias Medios"]
        st.bar_chart(df_delivery_time.set_index("Estado"))

st.divider()

# ============================================================
# Explorador de Dados
# ============================================================
st.header("Explorador de Dados")

tables = client.query("SELECT name FROM system.tables WHERE database = 'olist'").result_rows
table_names = [t[0] for t in tables]

selected_table = st.selectbox("Selecione uma tabela para explorar:", table_names)

if selected_table:
    df = client.query_df(f"SELECT * FROM olist.{selected_table} LIMIT 200")
    st.dataframe(df, use_container_width=True)
    st.caption(f"Mostrando ate 200 linhas de {selected_table}")
