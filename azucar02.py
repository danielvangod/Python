import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Configuración única
st.set_page_config(page_title="Control Glucosa", page_icon="🩸")

# 2. Conexión única a la nube
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Función para leer datos (evita duplicados)
def cargar_datos():
    return conn.read(ttl="0")

df = cargar_datos()

st.title("Solo un panel de control 🩸")

# 4. ÚNICO formulario de entrada
with st.form("registro_unico"):
    st.subheader("Nueva medición")
    c1, c2 = st.columns(2)
    with c1:
        f = st.date_input("Fecha", datetime.now())
    with c2:
        h = st.time_input("Hora", datetime.now())
    n = st.number_input("Nivel de azúcar (mg/dL)", min_value=0)
    
    boton = st.form_submit_button("Guardar Registro")

    if boton:
        nuevo = pd.DataFrame({"Fecha": [f.strftime("%d/%m/%Y")], "Hora": [h.strftime("%H:%M")], "Nivel": [n]})
        # Actualizamos la hoja de cálculo
        df_final = pd.concat([df, nuevo], ignore_index=True)
        conn.update(data=df_final)
        st.success("¡Guardado en la nube!")
        st.rerun() # Esto refresca la página para que el segundo cuadro no aparezca

# 5. Visualización
st.divider()
st.subheader("Historial")
st.dataframe(df, use_container_width=True)

st.subheader("Historial Sincronizado")
st.dataframe(df, use_container_width=True)
