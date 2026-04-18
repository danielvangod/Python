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

# --- CÁLCULO DE EDAD ---
fecha_nacimiento = datetime(1966, 8, 12)
edad = ahora_gt.year - fecha_nacimiento.year - ((ahora_gt.month, ahora_gt.day) < (fecha_nacimiento.month, fecha_nacimiento.day))

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.header("📊 Valores de Referencia")
    st.info("**Bajo:** ≤ 105 mg/dL")
    st.success("**Aceptable:** 106 - 140 mg/dL")
    st.warning("**Cuidar salud:** > 140 mg/dL")
    
    st.divider()
    
    # CUADRO DE INFORMACIÓN DEL PACIENTE
    st.header("👤 Ficha del Paciente")
    with st.container(border=True):
        st.write(f"**Nombre:** Armando Valencia Maldonado")
        st.write(f"**Edad:** {edad} años")
        
        if not df.empty:
            # Asegurar que el nivel sea numérico
            df['Nivel'] = pd.to_numeric(df['Nivel'], errors='coerce').fillna(0)
            ultimo_registro = df.iloc[-1]
            ultima_toma = int(ultimo_registro['Nivel'])
            
            st.write(f"**Última Glucosa:** {ultima_toma} mg/dL")
            # NUEVO: Fecha y hora de la última medición bajo el nivel
            st.markdown(f"<p style='font-size: 12px; color: gray; margin-top: -15px;'>Registrada: {ultimo_registro['Fecha']} a las {ultimo_registro['Hora']}</p>", unsafe_allow_html=True)
        
        st.write("**Contacto Emergencia:**")
        st.code("66311963", language=None)
    
    st.divider()
    st.caption("Sistema de monitoreo personalizado.")

# --- LÓGICA PARA EL TÍTULO DINÁMICO ---
nombre_paciente = "Armando Valencia Maldonado"
titulo_base = f"Bitácora - Paciente: {nombre_paciente}"

if not df.empty:
    ultima_toma = int(df['Nivel'].iloc[-1])
    
    if ultima_toma <= 105:
        color_titulo = "#3498db" # Azul
    elif 106 <= ultima_toma <= 140:
        color_titulo = "#27ae60" # Verde
    else:
        color_titulo = "#e74c3c" # Rojo
    
    st.markdown(f"<h1>{titulo_base} - <span style='color:{color_titulo}'>{ultima_toma} mg/dL</span></h1>", unsafe_allow_html=True)
else:
    st.title(titulo_base)

# --- FORMULARIO DE REGISTRO ---
with st.form("registro_glucosa"):
    st.subheader("Registro de Tomas de Glucosa")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        fecha = st.date_input("Fecha", ahora_gt.date())
    with col2:
        hora = st.time_input("Hora", ahora_gt.time())
    with col3:
        momento = st.selectbox("Momento de la toma", 
                              ["Ayunas", "Antes de comer", "Después de comer (2h)", "Antes de dormir", "Otro"])
    
    nivel = st.number_input("Nivel de azúcar (mg/dL)", min_value=0, step=1)
    
    btn_guardar = st.form_submit_button("Guardar Registro de toma")

    if btn_guardar:
        nuevo_dato = pd.DataFrame({
            "Fecha": [fecha.strftime("%d/%m/%Y")],
            "Hora": [hora.strftime("%I:%M %p")], 
            "Momento": [momento],
            "Nivel": [int(round(nivel))]
        })
        
        df_actualizado = pd.concat([df, nuevo_dato], ignore_index=True)
        conn.update(data=df_actualizado)
        
        if nivel <= 105:
            st.info(f"ℹ️ El nivel de {int(nivel)} mg/dL está muy bajo. Por favor, consulta con tu médico.")
        elif 106 <= nivel <= 140:
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
    df_filtrado = df.loc[mask].copy()

    # --- TABLA DE ESTADÍSTICAS ---
    st.subheader("📊 Resumen de Estadísticas")
    if not df_filtrado.empty:
        promedio = int(round(df_filtrado["Nivel"].mean()))
        
        fila_max = df_filtrado.loc[df_filtrado["Nivel"].idxmax()]
        max_valor = int(fila_max["Nivel"])
        max_info = f"{fila_max['Fecha']} - {fila_max['Momento']}"
        
        fila_min = df_filtrado.loc[df_filtrado["Nivel"].idxmin()]
        min_valor = int(fila_min["Nivel"])
        min_info = f"{fila_min['Fecha']} - {fila_min['Momento']}"

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Promedio", f"{promedio} mg/dL")
        m2.metric("Máxima", f"{max_valor} mg/dL")
        m3.metric("Mínima", f"{min_valor} mg/dL")
        m4.metric("Registros", len(df_filtrado))
        
        c1, c2, c3, c4 = st.columns(4)
        with c2:
            st.markdown(f"<p style='font-size: 13px; color: gray; margin-top: -20px;'>{max_info}</p>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<p style='font-size: 13px; color: gray; margin-top: -20px;'>{min_info}</p>", unsafe_allow_html=True)
        
        st.divider()

        def resaltar_niveles(val):
            try:
                val_int = int(val)
                if val_int <= 105: return 'color: #3498db; font-weight: bold'
                elif 106 <= val_int <= 140: return 'color: #27ae60; font-weight: bold'
                else: return 'color: #e74c3c; font-weight: bold'
            except: return None

        st.dataframe(df_filtrado.drop(columns=['Fecha_dt']).style.map(resaltar_niveles, subset=['Nivel']), use_container_width=True)

        st.subheader("📈 Tendencia en el tiempo")
        df_grafica = df_filtrado.copy()
        df_grafica['Fecha_Hora'] = df_grafica['Fecha'] + " " + df_grafica['Hora']
        st.line_chart(df_grafica.set_index('Fecha_Hora')['Nivel'])
    else:
        st.warning("No hay datos en el rango de fechas seleccionado.")
else:
    st.info("Aún no hay datos para mostrar.")
