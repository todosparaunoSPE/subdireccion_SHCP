# -*- coding: utf-8 -*-
"""
Created on Tue Jun 24 12:11:39 2025

@author: jahop
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from io import BytesIO

st.set_page_config(page_title="Herramienta Macroeconómica Mejorada", layout="wide")



st.markdown(
    """
    <style>
    /* Aumentar tamaño y estilo tabs */
    div[role="tablist"] > div[role="tab"] {
        font-size: 18px !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
        border: 2px solid #005f73 !important;
        border-radius: 10px 10px 0 0 !important;
        margin-right: 8px !important;
        color: #0a9396 !important;
        background-color: #e0fbfc !important;
        transition: background-color 0.3s ease, color 0.3s ease;
    }

    div[role="tablist"] > div[role="tab"][aria-selected="true"] {
        background-color: #005f73 !important;
        color: #e0fbfc !important;
        font-weight: 700 !important;
        border-bottom: 2px solid #e0fbfc !important;
    }
    </style>
    """, unsafe_allow_html=True
)



# --- Información inicial de la vacante ---
st.title("📊 Herramienta de Análisis Macroeconómico")

st.markdown("""
---
### Unidad de Planeación Económica de la Hacienda Pública  
**-Vacante-**

**Puesto:**  
- Subdirección

**Ubicación:**  
- Plaza Inn, Ciudad de México

**Principales responsabilidades:**  
- Dar seguimiento a la situación macroeconómica actual y a la evolución de los mercados financieros, tanto de México como a nivel internacional, para apoyar en la elaboración de notas informativas, reportes y presentaciones.  
- Análisis de la política monetaria y crediticia mediante el seguimiento y monitoreo de indicadores macroeconómicos.  
- Uso de herramientas estadísticas y econométricas.
---
""")

# --- Datos simulados ---
@st.cache_data
def generate_economic_data():
    dates = pd.date_range(start="2020-01-01", end=datetime.now(), freq='M')
    data = {
        'Fecha': dates,
        'PIB': np.cumsum(np.random.normal(1, 0.3, len(dates))) + 100,
        'Inflación': np.random.normal(4, 1, len(dates)),
        'Tasa de interés': np.random.normal(6, 0.5, len(dates)),
        'Desempleo': np.random.normal(3.5, 0.3, len(dates)),
        'Tipo de cambio': np.cumsum(np.random.normal(0.1, 0.5, len(dates))) + 20
    }
    return pd.DataFrame(data)

df = generate_economic_data()

# Parámetros mínimos para filtros
min_start_date = datetime(2020,1,1)
min_vol_date = datetime.now() - timedelta(days=180)

# --- Sidebar ---
st.sidebar.title("Configuración")
indicator = st.sidebar.selectbox("Indicador principal", df.columns[1:])
start_date = st.sidebar.date_input("Fecha inicio", datetime.now() - timedelta(days=365), min_value=min_start_date, max_value=datetime.now())
start_date_dt = pd.to_datetime(start_date)

# Ajuste para volatilidad (mínimo 6 meses atrás)
adjusted_start_date = start_date_dt if start_date_dt <= min_vol_date else min_vol_date

# Sliders simulación para varios indicadores
st.sidebar.markdown("---")
st.sidebar.subheader("Simulación de escenarios")
inflacion_adj = st.sidebar.slider("Ajustar Inflación (%)", -5.0, 5.0, 0.0, step=0.1)
tasa_adj = st.sidebar.slider("Ajustar Tasa de Interés (%)", -3.0, 3.0, 0.0, step=0.1)
desempleo_adj = st.sidebar.slider("Ajustar Desempleo (%)", -2.0, 2.0, 0.0, step=0.1)
tipo_cambio_adj = st.sidebar.slider("Ajustar Tipo de cambio", -3.0, 3.0, 0.0, step=0.1)

# Aplicar ajustes simulados
df_sim = df.copy()
df_sim["Inflación"] += inflacion_adj
df_sim["Tasa de interés"] += tasa_adj
df_sim["Desempleo"] += desempleo_adj
df_sim["Tipo de cambio"] += tipo_cambio_adj

filtered_df = df_sim[df_sim["Fecha"] >= start_date_dt]

# --- Funciones ---
def calculate_kpis(df_kpi, indicator):
    recent = df_kpi.iloc[-1][indicator]
    previous = df_kpi.iloc[-2][indicator]
    change_pct = ((recent - previous) / previous) * 100

    # Volatilidad última media móvil 6 meses
    vol_df = df_kpi[df_kpi["Fecha"] >= adjusted_start_date].copy()
    vol_df["Mes"] = vol_df["Fecha"].dt.to_period("M").astype(str)
    vol = vol_df.groupby("Mes")[indicator].std().mean()
    return recent, change_pct, vol

def kpi_color(change):
    if change > 2:
        return "green"
    elif change < -2:
        return "red"
    else:
        return "orange"

# --- Layout con Tabs ---
tab1, tab2, tab3 = st.tabs(["Análisis", "Simulación", "Exportar"])

with tab1:
    st.header("📊 Análisis de datos")
    st.markdown(f"Mostrando datos desde **{start_date_dt.strftime('%Y-%m-%d')}** para el indicador **{indicator}**")

    recent, change_pct, volatility = calculate_kpis(filtered_df, indicator)

    col1, col2, col3 = st.columns(3)
    col1.metric("Valor más reciente", f"{recent:.2f}", delta=None)
    col2.metric("Cambio % (último periodo)", f"{change_pct:.2f}%", delta=change_pct, delta_color="normal")
    col3.metric("Volatilidad (std. móvil 6 meses)", f"{volatility:.3f}")

    # Alertas visuales
    if change_pct > 5:
        st.success("El indicador muestra un aumento significativo.")
    elif change_pct < -5:
        st.error("El indicador ha caído considerablemente.")
    else:
        st.info("Cambio moderado en el indicador.")

    # Gráfico línea
    fig_line = px.line(filtered_df, x='Fecha', y=indicator, title=f"Evolución temporal de {indicator}", markers=True)
    st.plotly_chart(fig_line, use_container_width=True)

    # Histograma para distribución
    fig_hist = px.histogram(filtered_df, x=indicator, nbins=20, title=f"Distribución de valores de {indicator}")
    st.plotly_chart(fig_hist, use_container_width=True)

    # Matriz de correlación
    st.subheader("Matriz de correlación")
    corr = filtered_df.drop(columns=["Fecha"]).corr()
    fig_corr, ax = plt.subplots(figsize=(8,5))
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
    st.pyplot(fig_corr)

with tab2:
    st.header("🎛 Simulación de escenarios")
    st.markdown("Ajusta los sliders en la barra lateral para modificar los indicadores y observar el impacto en los datos.")

    st.dataframe(filtered_df.reset_index(drop=True))

    st.subheader("Gráficos con ajustes aplicados")
    fig_sim = px.line(filtered_df, x="Fecha", y=indicator, title=f"{indicator} con ajustes simulados", markers=True)
    st.plotly_chart(fig_sim, use_container_width=True)

with tab3:
    st.header("💾 Exportar datos filtrados")
    st.markdown("Descarga los datos actuales en formato CSV o Excel.")

    export_format = st.selectbox("Formato de archivo", ["CSV", "Excel"])

    def convert_df(df, format):
        if format == "CSV":
            return df.to_csv(index=False).encode('utf-8')
        else:
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Datos', index=False)
            return output.getvalue()

    data_to_export = filtered_df.reset_index(drop=True)
    data_file = convert_df(data_to_export, export_format)

    st.download_button(
        label=f"Descargar {export_format}",
        data=data_file,
        file_name=f"datos_macro.{ 'csv' if export_format == 'CSV' else 'xlsx' }",
        mime="text/csv" if export_format == "CSV" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Información de contacto en sidebar
st.sidebar.markdown("---")
st.sidebar.header("📌 Información de la vacante")
st.sidebar.write("""
**Puesto:** Subdirección  
**Ubicación:** Plaza Inn, Ciudad de México  
**Requisitos:**  
- Título en Economía, Actuaría o Matemáticas  
- 4+ años de experiencia  
- Dominio de Office, R, Bloomberg  
- Inglés avanzado  

**Beneficios:**  
- $32,000 netos  
- Aguinaldo 40 días  
""")

st.sidebar.markdown("---")
st.sidebar.header("Contacto")
st.sidebar.write("""
**Javier Horacio Pérez Ricárdez**  
Celular: +52 56 1056 4095
""")
