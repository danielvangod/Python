import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import pytz # Librería para manejo de zonas horarias

# --- CONFIGURACIÓN DE TIEMPO LOCAL ---
# Definimos la zona horaria de Guatemala
zona_gt = pytz.timezone('America/Guatemala')
ahora_gt = datetime.now(zona_gt)

st.set_page_config(page_title="Control Glucosa GT", page_icon="🩸")

# Conexión a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl="0")

st.title("Control de Glucosa - Guatemala 🇬🇹")

# --- FORMULARIO ---
with st.form("registro_glucosa"):
    st.subheader("Nueva Medición")
    
    col1, col2 = st.columns(2)
    with col1:
        # El calendario se abre con la fecha actual de GT
        fecha = st.date_input("Fecha", ahora_gt.date())
    with col2:
        # El reloj inicia con la hora exacta de GT
        hora = st.time_input("Hora", ahora_gt.time())
    
    nivel = st.number_input("Nivel de azúcar (mg/dL)", min_value=0, step=1)
    
    btn_guardar = st.form_submit_button("Guardar en la Nube")

    if btn_guardar:
        # Preparamos el nuevo registro
        nuevo_dato = pd.DataFrame({
            "Fecha": [fecha.strftime("%d/%m/%Y")],
            "Hora": [hora.strftime("%H:%M")],
            "Nivel": [nivel]
        })
        
        # Concatenamos y subimos a Google Sheets
        df_actualizado = pd.concat([df, nuevo_dato], ignore_index=True)
        conn.update(data=df_actualizado)
        
        st.success(f"Registrado con éxito (Hora local: {hora.strftime('%H:%M')})")
        st.rerun()

# --- VISUALIZACIÓN ---
st.divider()
st.subheader("Historial Sincronizado")
st.dataframe(df, use_container_width=True)

# Gráfica de tendencia
if not df.empty:
    st.subheader("Gráfica de Evolución")
    st.line_chart(df.set_index("Fecha")["Nivel"])
