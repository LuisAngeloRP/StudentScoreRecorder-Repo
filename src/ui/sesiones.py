# sesiones.py
import streamlit as st
from datetime import datetime
import pandas as pd
from ..utils.validators import validar_puntaje_maximo

def sesiones_ui(db):
    """Interfaz principal de sesiones y creación"""
    st.title("Gestión de Sesiones")
    
    # Configuración inicial
    indices_cursos, nombres_cursos = db.obtener_lista_cursos()
    if not indices_cursos:
        st.warning("No hay cursos disponibles. Por favor, cree un curso primero.")
        return
    
    # Sidebar para configuración
    with st.sidebar:
        st.markdown("### ⚙️ Configuración")
        curso_seleccionado = st.selectbox(
            "📚 Selecciona el curso",
            nombres_cursos,
            key="sesion_curso"
        )
        indice_curso = indices_cursos[nombres_cursos.index(curso_seleccionado)]
        
        # Gestión de alumnos
        st.markdown("### 👥 Gestión de Alumnos")
        with st.expander("➕ Agregar Nuevo Alumno"):
            with st.form("nuevo_alumno"):
                nuevo_apellido = st.text_input("Apellido")
                nuevo_nombre = st.text_input("Nombre")
                submitted = st.form_submit_button("Agregar Alumno")
                
                if submitted and nuevo_apellido and nuevo_nombre:
                    if db.agregar_alumno(indice_curso, nuevo_apellido, nuevo_nombre):
                        st.success("¡Alumno agregado exitosamente!")
                        st.rerun()
    
    # Pestañas principales
    tab1, tab2 = st.tabs(["📝 Nueva Sesión", "📊 Sesiones Guardadas"])
    
    with tab1:
        crear_sesion_actual(db, indice_curso)
    
    with tab2:
        mostrar_sesiones_guardadas(db, indice_curso, curso_seleccionado)

def crear_sesion_actual(db, indice_curso):
    """Maneja la creación de la sesión"""
    st.markdown("### 📝 Nueva Sesión")
    
    with st.form("crear_sesion"):
        col1, col2, col3 = st.columns([2,1,1])
        with col1:
            nombre_sesion = st.text_input("Nombre de la Sesión", "Sesión 1")
        with col2:
            puntaje_maximo = st.number_input("Puntaje Máximo", value=20, min_value=1)
        with col3:
            fecha_sesion = st.date_input("Fecha", datetime.now())
        
        submitted = st.form_submit_button("Crear Sesión", type="primary", use_container_width=True)
        
        if submitted:
            if nombre_sesion:
                sesion_id = db.crear_sesion(
                    indice_curso,
                    nombre_sesion,
                    puntaje_maximo,
                    fecha_sesion
                )
                if sesion_id:
                    st.success("¡Sesión creada exitosamente! 🎉")
                    st.info("Para registrar los puntajes, ve a la pestaña 'Sesiones Guardadas'")
                    st.form_submit_button("Crear otra sesión")
            else:
                st.error("Por favor, ingrese un nombre para la sesión")

def mostrar_sesiones_guardadas(db, indice_curso, curso_seleccionado):
    """Muestra el listado de sesiones con resultados y estadísticas"""
    df_sesiones = db.obtener_sesiones_curso(indice_curso)
    
    if df_sesiones.empty:
        st.info(f"No hay sesiones guardadas para el curso {curso_seleccionado}")
        return
    
    df_sesiones = df_sesiones.sort_values('fecha', ascending=False)
    
    for _, sesion in df_sesiones.iterrows():
        with st.container():
            df_puntajes = db.obtener_puntajes_sesion(sesion['id'])
            
            st.markdown(f"""
                <div style='
                    background-color: white;
                    padding: 20px;
                    border-radius: 10px;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                '>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <h3 style='margin: 0;'>{sesion['nombre']}</h3>
                        <span style='color: #666;'>{sesion['fecha']}</span>
                    </div>
                    <p style='margin: 10px 0;'>Puntaje máximo: {sesion['puntaje_maximo']} ✨</p>
                </div>
            """, unsafe_allow_html=True)
            
            if not df_puntajes.empty:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Promedio", f"{df_puntajes['Puntaje'].mean():.1f}")
                with col2:
                    st.metric("Máximo", int(df_puntajes['Puntaje'].max()))
                with col3:
                    st.metric("Mínimo", int(df_puntajes['Puntaje'].min()))
                
                with st.expander("Ver detalles completos"):
                    st.dataframe(
                        df_puntajes,
                        column_config={
                            "Apellido": "Apellido",
                            "Nombre": "Nombre",
                            "Puntaje": st.column_config.NumberColumn(
                                "Puntaje",
                                format="%d ✨"
                            )
                        },
                        hide_index=True
                    )
                    
                    st.write("### Distribución de puntajes")
                    hist_data = df_puntajes['Puntaje'].value_counts().sort_index()
                    st.bar_chart(hist_data)
            
            st.markdown("---")