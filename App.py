import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import yfinance as yf

# Configuración para móvil
st.set_page_config(page_title="Mi Bolsa App", layout="centered")

st.title("📊 Mi Analizador de Bolsa")

# Selector de Acción
ticker = st.text_input(
    "Buscar Ticker (ej: AAPL, MSFT, NVDA, SAN.MC):", "AAPL"
).upper()

if ticker:
    with st.spinner("Cargando datos del mercado..."):
        # Descargamos 2 años de datos para que la Media Móvil 200 funcione siempre
        df = yf.download(ticker, period="2y", interval="1d")

    if df.empty:
        st.error(
            "No se encontraron datos para ese Ticker. Revisa si está bien escrito."
        )
    else:
        # Aplanar columnas de yfinance si vienen en formato doble
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Calcular Media Móvil 200 y RSI
        df["SMA200"] = df["Close"].rolling(window=200).mean()

        delta = df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df["RSI"] = 100 - (100 / (1 + rs))

        # Nos quedamos con los últimos 6 meses para mostrar un gráfico claro
        df_plot = df.tail(130)

        # DIBUJAR GRÁFICOS
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.08,
            row_heights=[0.7, 0.3],
        )

        # Velas Japonesas
        fig.add_trace(
            go.Candlestick(
                x=df_plot.index,
                open=df_plot["Open"],
                high=df_plot["High"],
                low=df_plot["Low"],
                close=df_plot["Close"],
                name="Precio",
            ),
            row=1,
            col=1,
        )

        # Media Móvil 200
        fig.add_trace(
            go.Scatter(
                x=df_plot.index,
                y=df_plot["SMA200"],
                line=dict(color="orange", width=2),
                name="SMA 200",
            ),
            row=1,
            col=1,
        )

        # RSI
        fig.add_trace(
            go.Scatter(
                x=df_plot.index,
                y=df_plot["RSI"],
                line=dict(color="purple", width=2),
                name="RSI",
            ),
            row=2,
            col=1,
        )

        fig.update_layout(
            xaxis_rangeslider_visible=False,
            height=500,
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

        # CALCULADORA DE RIESGO
        st.subheader("🛡️ Calculadora de Riesgo")
        col1, col2 = st.columns(2)

        precio_actual = float(df["Close"].iloc[-1])
        col1.metric("Precio Actual", f"${precio_actual:.2f}")

        capital = col2.number_input("Tu Capital ($):", value=500, step=50)
        riesgo_pct = col1.slider("Riesgo máximo (%):", 1, 5, 2)
        stop_loss = col2.number_input(
            "Stop Loss ($):", value=round(precio_actual * 0.95, 2)
        )

        riesgo_dolares = capital * (riesgo_pct / 100)
        riesgo_por_accion = precio_actual - stop_loss

        if riesgo_por_accion > 0:
            num_acciones = int(riesgo_dolares / riesgo_por_accion)
            inversion_total = num_acciones * precio_actual

            st.info(f"""
            👉 **Recomendación para bajo riesgo:**
            - Compra máximo: **{num_acciones} acciones**
            - Inversión total requerida: **${inversion_total:.2f}**
            - Si salta el Stop Loss, solo perderás: **${riesgo_dolares:.2f}** ({riesgo_pct}%)
            """)
        else:
            st.warning("El Stop Loss debe ser menor que el precio actual.")
