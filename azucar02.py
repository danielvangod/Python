import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import pytz
import time

# --- CONFIGURACIÓN DE TIEMPO LOCAL (GUATEMALA) ---
zona_gt = pytz.timezone('America/Guatemala')
ahora_gt = datetime.now(zona_gt)

st.set_page_config(page_title="Bítacora de Glucosa", page_icon="🩸")

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl="0")

st.title("Bítacora - Paciente: Armando Valencia", page_icon="🩸")

# --- FORMULARIO DE REGISTRO ---
with st.form("registro_glucosa"):
    st.subheader("Nueva Medición")
    
    col1, col2 = st.columns(2)
    with col1:
        fecha = st.date_input("Fecha", ahora_gt.date())
    with col2:
        hora = st.time_input("Hora", ahora_gt.time())
    
    nivel = st.number_input("Nivel de azúcar (mg/dL)", min_value=0, step=1)
    
    btn_guardar = st.form_submit_button("Guardar en la Nube")

    if btn_guardar:
        nuevo_dato = pd.DataFrame({
            "Fecha": [fecha.strftime("%d/%m/%Y")],
            "Hora": [hora.strftime("%H:%M")],
            "Nivel": [int(nivel)]
        })
        
        # Sincronización con la nube
        df_actualizado = pd.concat([df, nuevo_dato], ignore_index=True)
        conn.update(data=df_actualizado)
        
        # --- LÓGICA DE MENSAJES ---
        if nivel < 140:
            st.balloons()
            st.success(f"✅ ¡Felicidades! Tu nivel de {nivel} mg/dL está en un rango excelente. ¡Sigue así!")
        else:
            st.warning(f"⚠️ Atención: Tu nivel es de {nivel} mg/dL. Es importante controlar tu glucosa y seguir indicaciones médicas.")
        
        time.sleep(3)
        st.rerun()

# --- VISUALIZACIÓN CON ESTILO ---
st.divider()
st.subheader("Historial de Registros")

if not df.empty:
    # Función para aplicar colores a la columna 'Nivel'
    def resaltar_niveles(val):
        try:
            val_int = int(val)
            color = 'red' if val_int >= 140 else 'green'
            return f'color: {color}; font-weight: bold'
        except:
            return None

    # Aplicamos el estilo a la tabla
    # Nota: Usamos .style para que se vea profesional
    st.dataframe(df.style.map(resaltar_niveles, subset=['Nivel']), use_container_width=True)

    # Gráfica de línea rápida
    st.subheader("Tendencia")
    st.line_chart(df["Nivel"])
else:
    st.info("Aún no hay datos para mostrar.")
