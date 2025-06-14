import streamlit as st
import pandas as pd
import plotly.express as px

# Cargar datos
df = pd.read_csv("dataset_ventas_lacteos_2024.csv")
df["Fecha"] = pd.to_datetime(df["Fecha"], dayfirst=True)

# Asegurar que valores son numéricos
df["Valor total (USD)"] = pd.to_numeric(df["Valor total (USD)"], errors="coerce")
df["Precio unitario (USD)"] = pd.to_numeric(df["Precio unitario (USD)"], errors="coerce")
df["Cantidad comprada"] = pd.to_numeric(df["Cantidad comprada"], errors="coerce")

# Configurar página
st.set_page_config(page_title="Ventas de Lácteos 2024", layout="wide")
st.title("Dashboard de Ventas de Lácteos 2024")

# Sidebar: filtros
with st.sidebar:
    st.header("Filtros Básicos")
    estados = st.multiselect("Estado", options=df["Estado"].unique(), default=df["Estado"].unique())
    categorias = st.multiselect("Categoría", options=df["Categoría"].unique(), default=df["Categoría"].unique())
    formas_pago = st.multiselect("Forma de pago", options=df["Forma de pago"].unique(), default=df["Forma de pago"].unique())

    st.header("Filtros Avanzados")
    # Filtro por rango de fechas
    min_date = df["Fecha"].min().date()
    max_date = df["Fecha"].max().date()
    date_range = st.date_input(
        "Rango de fechas",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

    # Filtro por rango de precios unitarios
    min_price = float(df["Precio unitario (USD)"].min())
    max_price = float(df["Precio unitario (USD)"].max())
    price_range = st.slider(
        "Rango de precios unitarios (USD)",
        min_price, max_price, (min_price, max_price)
    )

    min_sales = st.number_input("Ventas mínimas por producto (USD)",
                                min_value=0,
                                value=0,
                                step=100)

# Filtrar datos
df_filtrado = df[
    (df["Estado"].isin(estados)) &
    (df["Categoría"].isin(categorias)) &
    (df["Forma de pago"].isin(formas_pago)) &
    (df["Fecha"].dt.date >= date_range[0]) &
    (df["Fecha"].dt.date <= date_range[1]) &
    (df["Precio unitario (USD)"] >= price_range[0]) &
    (df["Precio unitario (USD)"] <= price_range[1])
    ].copy()

if min_sales > 0:
    ventas_por_producto = df_filtrado.groupby("Producto")["Valor total (USD)"].sum()
    productos_seleccionados = ventas_por_producto[ventas_por_producto >= min_sales].index
    df_filtrado = df_filtrado[df_filtrado["Producto"].isin(productos_seleccionados)]

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Ventas Totales", f"${df_filtrado['Valor total (USD)'].sum():,.2f}")
col2.metric("Unidades Vendidas", f"{df_filtrado['Cantidad comprada'].sum():,}")
col3.metric("Precio Promedio Unitario", f"${df_filtrado['Precio unitario (USD)'].mean():.2f}")

st.markdown("---")

# Primera fila de gráficos
col1, col2 = st.columns(2)
with col1:
    st.subheader("Ventas Totales por Estado")
    ventas_estado = df_filtrado.groupby("Estado")["Valor total (USD)"].sum().reset_index().sort_values("Valor total (USD)", ascending=False)
    fig1 = px.bar(ventas_estado, x="Estado", y="Valor total (USD)", color="Estado")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Distribución por Categoría")
    fig2 = px.pie(df_filtrado, names="Categoría", values="Valor total (USD)", hole=0.4)
    st.plotly_chart(fig2, use_container_width=True)

# Segunda fila de gráficos
col1, col2 = st.columns(2)
with col1:
    st.subheader("Evolución Mensual de Ventas")
    df_filtrado["Mes"] = df_filtrado["Fecha"].dt.to_period("M").astype(str)
    ventas_mes = df_filtrado.groupby("Mes")["Valor total (USD)"].sum().reset_index()
    fig3 = px.line(ventas_mes, x="Mes", y="Valor total (USD)", markers=True)
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.subheader("Top 10 Productos Más Vendidos")
    top_productos = df_filtrado.groupby("Producto")["Valor total (USD)"].sum().reset_index().sort_values("Valor total (USD)", ascending=False).head(10)
    fig4 = px.bar(top_productos, x="Valor total (USD)", y="Producto", orientation="h", color="Producto")
    st.plotly_chart(fig4, use_container_width=True)

# Tercera fila de gráficos
st.subheader("Relación Precio vs Cantidad Vendida")
fig5 = px.scatter(
    df_filtrado,
    x="Precio unitario (USD)",
    y="Cantidad comprada",
    color="Categoría",
    size="Valor total (USD)",
    hover_name="Producto",
)
st.plotly_chart(fig5, use_container_width=True)

# Mapa de ventas
st.subheader("Mapa de Ventas por Ciudad")
ciudades_coords = {
    "Austin": (30.2672, -97.7431),
    "Boston": (42.3601, -71.0589),
    "Buffalo": (42.8864, -78.8784),
    "Dallas": (32.7767, -96.7970),
    "Houston": (29.7604, -95.3698),
    "Jacksonville": (30.3322, -81.6557),
    "Los Angeles": (34.0522, -118.2437),
    "Lowell": (42.6334, -71.3162),
    "Miami": (25.7617, -80.1918),
    "New York City": (40.7128, -74.0060),
    "Orlando": (28.5383, -81.3792),
    "Rochester": (43.1566, -77.6088),
    "San Antonio": (29.4241, -98.4936),
    "San Diego": (32.7157, -117.1611),
    "San Francisco": (37.7749, -122.4194),
    "San Jose": (37.3382, -121.8863),
    "Springfield": (42.1015, -72.5898),
    "Tampa": (27.9506, -82.4572),
    "Worcester": (42.2626, -71.8023),
    "Yonkers": (40.9312, -73.8988)
}

df_filtrado["Lat"] = df_filtrado["Ciudad"].map(lambda x: ciudades_coords.get(x.strip(), (None, None))[0])
df_filtrado["Lon"] = df_filtrado["Ciudad"].map(lambda x: ciudades_coords.get(x.strip(), (None, None))[1])

ventas_ciudad = df_filtrado.dropna(subset=["Lat", "Lon"]).groupby("Ciudad").agg({
    "Valor total (USD)": "sum",
    "Lat": "first",
    "Lon": "first"
}).reset_index()

if not ventas_ciudad.empty:
    fig6 = px.scatter_map(
        ventas_ciudad,
        lat="Lat",
        lon="Lon",
        size="Valor total (USD)",
        color="Valor total (USD)",
        hover_name="Ciudad",
        size_max=15,
        zoom=3,
        height=500,
        color_continuous_scale=px.colors.sequential.Viridis
    )
    fig6.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig6, use_container_width=True)
else:
    st.warning("No hay datos con coordenadas válidas para el mapa")

# Gráfico adicional: Ventas por día de la semana
st.subheader("Ventas por Día de la Semana")
df_filtrado["Dia Semana"] = df_filtrado["Fecha"].dt.day_name(locale='es')
dias_orden = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
ventas_dia = df_filtrado.groupby("Dia Semana")["Valor total (USD)"].sum().reindex(dias_orden).reset_index()
fig7 = px.bar(ventas_dia, x="Dia Semana", y="Valor total (USD)", color="Dia Semana")
st.plotly_chart(fig7, use_container_width=True)

# Tabla resumen
with st.expander("Ver datos detallados"):
    st.dataframe(df_filtrado.sort_values("Valor total (USD)", ascending=False))