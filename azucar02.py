import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Control de Glucosa", page_icon="🩸")

st.title("Control Diario de Glucosa")

# Inicializar o cargar datos
if 'df' not in st.session_state:
    try:
        st.session_state.df = pd.read_csv("mis_datos_glucosa.csv")
    except FileNotFoundError:
        st.session_state.df = pd.DataFrame(columns=["Fecha", "Hora", "Nivel"])

# --- FORMULARIO DE INGRESO ---
with st.expander("➕ Ingresar Nueva Toma", expanded=True):
    with st.form("formulario_glucosa"):
        col1, col2 = st.columns(2)
        with col1:
            fecha = st.date_input("Fecha de la toma", datetime.now())
        with col2:
            hora = st.time_input("Hora de la toma", datetime.now())
        
        nivel = st.number_input("Nivel de azúcar (mg/dL)", min_value=0, step=1)
        
        enviado = st.form_submit_button("Guardar Registro")
        
        if enviado:
            nuevo_dato = pd.DataFrame({
                "Fecha": [fecha.strftime("%d/%m/%Y")],
                "Hora": [hora.strftime("%H:%M")],
                "Nivel": [nivel]
            })
            st.session_state.df = pd.concat([st.session_state.df, nuevo_dato], ignore_index=True)
            st.session_state.df.to_csv("mis_datos_glucosa.csv", index=False)
            st.success("¡Datos guardados con éxito!")

# --- VISUALIZACIÓN Y FILTROS ---
if not st.session_state.df.empty:
    st.subheader("Historial y Tendencias")
    
    # Gráfico de línea
    fig, ax = plt.subplots()
    ax.plot(st.session_state.df["Nivel"], marker='o', linestyle='-', color='#FF4B4B')
    ax.set_ylabel("mg/dL")
    ax.set_title("Evolución de Glucosa")
    st.pyplot(fig)
    
    # Tabla de datos
    st.dataframe(st.session_state.df, use_container_width=True)
    
    # Botón para descargar Excel (CSV compatible)
    csv = st.session_state.df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Reporte Completo",
        data=csv,
        file_name='reporte_glucosa.csv',
        mime='text/csv',
    )
else:
    st.info("Aún no hay datos registrados. Usa el formulario de arriba.")

    # segundo codigo que conecta a la google sheets

    import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Control de Glucosa en la Nube", page_icon="🩸")

st.title("Sistema de Control de Glucosa Cloud")

# Crear conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Leer datos existentes
df = conn.read(ttl="0") # ttl=0 para que siempre refresque los datos

with st.form("formulario_cloud"):
    col1, col2 = st.columns(2)
    with col1:
        fecha = st.date_input("Fecha", datetime.now())
    with col2:
        hora = st.time_input("Hora", datetime.now())
    
    nivel = st.number_input("Nivel (mg/dL)", min_value=0)
    boton = st.form_submit_button("Guardar en la Nube")

    if boton:
        nuevo_registro = pd.DataFrame({
            "Fecha": [fecha.strftime("%d/%m/%Y")],
            "Hora": [hora.strftime("%H:%M")],
            "Nivel": [nivel]
        })
        
        # Combinar con datos viejos y actualizar la nube
        df_actualizado = pd.concat([df, nuevo_registro], ignore_index=True)
        conn.update(data=df_actualizado)
        st.success("¡Datos sincronizados con Google Sheets!")
        st.rerun()

st.subheader("Historial Sincronizado")
st.dataframe(df, use_container_width=True)

streamlit
pandas
matplotlib
st-gsheets-connection
