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

st.title("Bitácora - Paciente: Armando Valencia Maldonado")

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
    
    nivel = st.number_input("Nivel de azúcar (mg/dL)", min_value=0, step=1)
    
    btn_guardar = st.form_submit_button("Guardar en la Nube")

    if btn_guardar:
        nuevo_dato = pd.DataFrame({
            "Fecha": [fecha.strftime("%d/%m/%Y")],
            "Hora": [hora.strftime("%I:%M %p")], 
            "Momento": [momento],
            "Nivel": [int(round(nivel))]
        })
        
        df_actualizado = pd.concat([df, nuevo_dato], ignore_index=True)
        conn.update(data=df_actualizado)
        
        # --- NUEVA LÓGICA DE MENSAJES SEGÚN RANGOS ---
        if nivel <= 105:
            st.info(f"ℹ️ El nivel de {int(nivel)} mg/dL está muy bajo. Por favor, consulta con tu médico.")
        elif 106 <= nivel <= 120:
            st.balloons()
            st.success(f"✅ ¡Excelente! Tu nivel de {int(nivel)} mg/dL es aceptable. ¡Sigue así!")
        else:
            st.warning(f"⚠️ Atención: Tu nivel es de {int(nivel)} mg/dL. Debes cuidar tu alimentación y hacer más ejercicio.")
        
        time.sleep(3)
        st.rerun()

# --- SECCIÓN DE FILTROS Y ESTADÍSTICAS ---
st.divider()

if not df.empty:
    df['Nivel'] = pd.to_numeric(df['Nivel'], errors='coerce').fillna(0).round(0).astype(int)
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
        promedio = int(round(df_filtrado["Nivel"].mean()))
        maximo = int(df_filtrado["Nivel"].max())
        minimo = int(df_filtrado["Nivel"].min())

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Promedio", f"{promedio} mg/dL")
        m2.metric("Máxima", f"{maximo} mg/dL")
        m3.metric("Mínima", f"{minimo} mg/dL")
        m4.metric("Registros", len(df_filtrado))
        
        # --- TABLA CON ESTILO DE COLORES ACTUALIZADO ---
        def resaltar_niveles(val):
            try:
                val_int = int(val)
                if val_int <= 105:
                    return 'color: #3498db; font-weight: bold' # Azul para bajo
                elif 106 <= val_int <= 120:
                    return 'color: #27ae60; font-weight: bold' # Verde para aceptable
                else:
                    return 'color: #e74c3c; font-weight: bold' # Rojo para alto (>120)
            except: return None

        st.dataframe(df_filtrado.style.map(resaltar_niveles, subset=['Nivel']), use_container_width=True)

        # --- GRÁFICA DE EVOLUCIÓN ---
        st.subheader("📈 Tendencia en el tiempo")
        df_grafica = df_filtrado.copy()
        df_grafica['Fecha_Hora'] = df_grafica['Fecha'] + " " + df_grafica['Hora']
        st.line_chart(df_grafica.set_index('Fecha_Hora')['Nivel'])
    else:
        st.warning("No hay datos en el rango de fechas seleccionado.")
else:
    st.info("Aún no hay datos para mostrar.")
