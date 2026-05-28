import streamlit as st
import pandas as pd
import clickhouse_connect
import os

# Configuração da página
st.set_page_config(
    page_title="Olist SRE Analytics - Aula 04",
    page_icon="📦",
    layout="wide"
)

def get_client():
    """Retorna o cliente do ClickHouse baseado em variáveis de ambiente."""
    return clickhouse_connect.get_client(
        host=os.getenv('CLICKHOUSE_HOST', 'clickhouse'),
        port=int(os.getenv('CLICKHOUSE_PORT', 8123)),
        username=os.getenv('CLICKHOUSE_USER', 'default'),
        password=os.getenv('CLICKHOUSE_PASSWORD', '')
    )

@st.cache_data(ttl=60)
def load_data(top_n):
    """Consulta a view v_top_products com cache de 60 segundos."""
    client = get_client()
    query = f"SELECT * FROM olist_raw.v_top_products LIMIT {top_n}"
    return client.query_df(query)

@st.cache_data(ttl=60)
def get_metrics():
    """Consulta métricas agregadas da view."""
    client = get_client()
    query = """
    SELECT 
        sum(revenue) as total_revenue,
        sum(total_orders) as total_orders
    FROM olist_raw.v_top_products
    """
    return client.query_df(query)

# Título Principal
st.title("📊 Dashboard de Performance Olist (Local)")
st.markdown("---")

# Sidebar para Filtros
st.sidebar.header("Filtros")
top_n = st.sidebar.slider("Quantidade de Produtos (Top N)", 5, 50, 10)

try:
    # Carregamento de dados
    df = load_data(top_n)
    metrics = get_metrics()

    if df.empty:
        st.warning("⚠️ A ingestão foi concluída, mas a view 'v_top_products' não retornou dados. Verifique se os CSVs de itens e produtos foram carregados corretamente.")
    else:
        # Linha de Métricas
        total_rev = metrics['total_revenue'].iloc[0] or 0
        total_ord = metrics['total_orders'].iloc[0] or 0

        col1, col2 = st.columns(2)
        col1.metric("Receita Total", f"R$ {total_rev:,.2f}")
        col2.metric("Total de Pedidos", f"{int(total_ord):,}")

        st.markdown("---")

        # Gráfico e Tabela
        tab1, tab2 = st.tabs(["📈 Gráfico de Receita", "📄 Dados Detalhados"])

        with tab1:
            st.subheader(f"Top {top_n} Produtos por Receita")
            df_chart = df.copy()
            df_chart['short_id'] = df_chart['product_id'].str[:8]
            st.bar_chart(df_chart.set_index('short_id')['revenue'])

        with tab2:
            st.subheader("Tabela de Produtos")
            st.dataframe(
                df.style.format({
                    'revenue': 'R$ {:,.2f}',
                    'total_orders': '{:,}',
                    'total_items': '{:,}'
                }),
                use_container_width=True
            )

except Exception as e:
    st.error("❌ **Erro de Conexão ou Inicialização**")
    st.info("""
        O dashboard não conseguiu acessar os dados. Certifique-se que:
        1. A stack Docker está rodando (`docker-compose up`).
        2. O Ingestor já processou os arquivos CSV do MinIO.
        3. A view `olist_raw.v_top_products` foi criada com sucesso.
    """)
    with st.expander("Ver detalhes técnicos do erro"):
        st.code(str(e))

# Rodapé de SRE
st.sidebar.markdown("---")
st.sidebar.caption("Status do Pipeline: 🟢 Operacional")
if st.sidebar.button('Forçar Atualização'):
    st.cache_data.clear()
    st.rerun()
