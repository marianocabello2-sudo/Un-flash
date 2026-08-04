¡Buenísimo que ya tengas la cuenta y el repositorio listo! Estás a la mitad del
camino.

No te preocupes, app.py es simplemente un archivo de texto donde pegamos la
"receta" (el código Python) de tu aplicación. El nombre .py le indica al
servidor que ese archivo contiene código de Python.

Lo mejor es que puedes crearlo directamente desde la página web de GitHub, sin
instalar nada en tu ordenador.

Sigue estos pasos dentro de tu repositorio en GitHub:

Paso 1: Crear el archivo app.py

1.  Dentro de tu repositorio en GitHub, busca un botón arriba a la derecha que
    dice "Add file" (Añadir archivo) y haz clic en "Create new file" (Crear
    nuevo archivo).
2.  En la casilla que dice Name your file... escribe exactamente: app.py
3.  En el cuadro grande de texto de abajo, copia y pega todo este código:

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import yfinance as yf

# Configuración para móvil
st.set_page_config(page_title="Mi Bolsa App", layout="centered")

st.title("📊 Mi Analizador de Bolsa")

# Selector de Acción
ticker = st.text_input("Buscar Ticker (ej: AAPL, MSFT, NVDA, SAN.MC):", "AAPL")
periodo = st.selectbox("Periodo:", ["3m", "6m", "1y"], index=1)

if ticker:
    # Descargar datos
    df = yf.download(ticker, period=periodo, interval="1d")

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Calcular Media Móvil 200 y RSI
    df["SMA200"] = df["Close"].rolling(window=200).mean()

    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    # DIBUJAR GRÁFICOS
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.7, 0.3],
    )

    # Velas Japonesas
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Precio",
        ),
        row=1,
        col=1,
    )

    # Media Móvil 200
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["SMA200"],
            line=dict(color="orange", width=2),
            name="SMA 200",
        ),
        row=1,
        col=1,
    )

    # RSI
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["RSI"],
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

4.  Baja hasta el final de la página y haz clic en el botón verde "Commit
    changes..." (Guardar cambios).

Paso 2: Crear el archivo requirements.txt

Este segundo archivo le dice al servidor qué herramientas necesita descargar
para ejecutar tu app.

1.  De nuevo en tu repositorio, haz clic en "Add file" -> "Create new file".
2.  De nombre ponle exactamente: requirements.txt
3.  En el cuadro de texto pega solo estas 4 líneas:
    streamlit
    yfinance
    plotly
    pandas
4.  Baja y haz clic en el botón verde "Commit changes...".

¡Y listo! Ahora en la pantalla principal de tu repositorio deberías ver los dos
archivos guardados: app.py y requirements.txt.

¿Pudiste crearlos? Si es así, el siguiente paso es conectar esto con Streamlit
para que nos dé el enlace de tu app móvil.
