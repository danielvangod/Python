import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import pytz
import time

# --- CONFIGURACIÓN DE TIEMPO LOCAL (GUATEMALA) ---
zona_gt = pytz.timezone('America/Guatemala')
ahora_gt = datetime.now(zona_gt)

st.set_page_config(page_title="Bitácora de Glucosa", page_icon="🩸", layout="wide")

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl="0")

st.title("Bitácora - Paciente: Armando Valencia")

# --- FORMULARIO DE REGISTRO ---
with st.form("registro_glucosa"):
    st.subheader("Nueva Medición")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        fecha = st.date_input("Fecha", ahora_gt.date())
    with col2:
        hora = st.time_input("Hora", ahora_gt.time())
    with col3:
        momento = st.selectbox("Momento de la toma", 
                              ["Ayunas", "Antes de comer", "Después de comer (2h)", "Antes de dormir", "Otro"])
    
    # Usamos step=1 para que el selector solo sugiera enteros
    nivel = st.number_input("Nivel de azúcar (mg/dL)", min_value=0, step=1)
    
    btn_guardar = st.form_submit_button("Guardar en la Nube")

    if btn_guardar:
        nuevo_dato = pd.DataFrame({
            "Fecha": [fecha.strftime("%d/%m/%Y")],
            "Hora": [hora.strftime("%H:%M")],
            "Momento": [momento],
            "Nivel": [int(round(nivel))] # Redondeamos al guardar
        })
        
        df_actualizado = pd.concat([df, nuevo_dato], ignore_index=True)
        conn.update(data=df_actualizado)
        
        if nivel < 140:
            st.balloons()
            st.success(f"✅ ¡Felicidades! Tu nivel de {int(nivel)} mg/dL es excelente.")
        else:
            st.warning(f"⚠️ Atención: Tu nivel es de {int(nivel)} mg/dL. Controla tu alimentación.")
        
        time.sleep(2)
        st.rerun()

# --- SECCIÓN DE FILTROS Y ESTADÍSTICAS ---
st.divider()

if not df.empty:
    # Aseguramos que la columna Nivel sea numérica y sin decimales para los cálculos
    df['Nivel'] = pd.to_numeric(df['Nivel'], errors='coerce').fillna(0).round(0).astype(int)
    
    # Convertir columna Fecha a objeto datetime para poder filtrar
    df['Fecha_dt'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y')
    
    st.subheader("🔍 Filtros e Historial")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        fecha_inicio = st.date_input("Desde", ahora_gt.date() - timedelta(days=7))
    with col_f2:
        fecha_fin = st.date_input("Hasta", ahora_gt.date())

    mask = (df['Fecha_dt'].dt.date >= fecha_inicio) & (df['Fecha_dt'].dt.date <= fecha_fin)
    df_filtrado = df.loc[mask].drop(columns=['Fecha_dt'])

    # --- TABLA DE ESTADÍSTICAS ---
    st.subheader("📊 Resumen de Estadísticas (Rango Seleccionado)")
    if not df_filtrado.empty:
        # Calculamos y redondeamos a enteros
        promedio = int(round(df_filtrado["Nivel"].mean()))
        maximo = int(df_filtrado["Nivel"].max())
        minimo = int(df_filtrado["Nivel"].min())
        total_registros = len(df_filtrado)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Promedio", f"{promedio} mg/dL")
        m2.metric("Máxima", f"{maximo} mg/dL")
        m3.metric("Mínima", f"{minimo} mg/dL")
        m4.metric("Registros", total_registros)
        
        # --- TABLA CON ESTILO ---
        def resaltar_niveles(val):
            try:
                val_int = int(val)
                color = 'red' if val_int >= 140 else 'green'
                return f'color: {color}; font-weight: bold'
            except: return None

        # Mostramos la tabla asegurando enteros en la visualización
        st.dataframe(df_filtrado.style.map(resaltar_niveles, subset=['Nivel']), use_container_width=True)

        # --- GRÁFICA DE EVOLUCIÓN ---
        st.subheader("📈 Tendencia en el tiempo")
        df_grafica = df
