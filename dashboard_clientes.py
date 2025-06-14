import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración inicial
st.set_page_config(page_title="Dashboard de Clientes", layout="wide")

st.title("Dashboard Interactivo de Clientes y Compras")

# Cargar datos
@st.cache_data
def cargar_datos():
    return pd.read_csv("clientes.csv")

df = cargar_datos()

# Sidebar: Filtros
st.sidebar.header("Filtros")

# Filtros múltiples
categorias = st.sidebar.multiselect("Categoría", df["Category"].unique(), default=df["Category"].unique())
generos = st.sidebar.multiselect("Género", df["Gender"].unique(), default=df["Gender"].unique())
temporadas = st.sidebar.multiselect("Temporada", df["Season"].unique(), default=df["Season"].unique())
rango_edad = st.sidebar.slider("Edad", int(df["Age"].min()), int(df["Age"].max()), (18, 60))
rango_compra = st.sidebar.slider("Monto de compra (USD)", float(df["Purchase Amount (USD)"].min()),
                                 float(df["Purchase Amount (USD)"].max()), (0.0, 100.0))
solo_suscriptores = st.sidebar.checkbox("Solo suscriptores", value=False)

# Aplicar filtros
df_filtrado = df[
    (df["Category"].isin(categorias)) &
    (df["Gender"].isin(generos)) &
    (df["Season"].isin(temporadas)) &
    (df["Age"].between(*rango_edad)) &
    (df["Purchase Amount (USD)"].between(*rango_compra))
    ]

if solo_suscriptores:
    df_filtrado = df_filtrado[df_filtrado["Subscription Status"] == "Yes"]

# KPIs
st.markdown("### Indicadores Clave")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total ventas", f"${df_filtrado['Purchase Amount (USD)'].sum():,.2f}")
col2.metric("Promedio reseñas", f"{df_filtrado['Review Rating'].mean():.2f}")
col3.metric("Clientes únicos", df_filtrado["Customer ID"].nunique())
porc_subs = (df_filtrado["Subscription Status"] == "Yes").mean() * 100
col4.metric("% Suscriptores", f"{porc_subs:.1f}%")

# Visualizaciones
st.markdown("### Visualizaciones")

col5, col6 = st.columns(2)
with col5:
    fig1 = px.histogram(df_filtrado, x="Location", color="Category",
                        title="Compras por Ubicación", barmode="group")
    st.plotly_chart(fig1, use_container_width=True)

with col6:
    fig2 = px.pie(df_filtrado, names="Payment Method", title="Métodos de Pago")
    st.plotly_chart(fig2, use_container_width=True)

# Gráfico de dispersión
st.markdown("### Dispersión Edad vs Monto de Compra")
fig3 = px.scatter(df_filtrado, x="Age", y="Purchase Amount (USD)", color="Gender",
                  size="Review Rating", hover_data=["Item Purchased", "Location"])
st.plotly_chart(fig3, use_container_width=True)

# Histograma frecuencia de compras
st.markdown("### Frecuencia de Compras")
fig4 = px.histogram(df_filtrado, x="Frequency of Purchases", color="Gender")
st.plotly_chart(fig4, use_container_width=True)

# Tabla y exportación
st.markdown("### Datos filtrados")
st.dataframe(df_filtrado)

# Botón para descarga
st.download_button("Descargar CSV filtrado", df_filtrado.to_csv(index=False), file_name="clientes_filtrados.csv")