import streamlit as st
from datetime import datetime
import pandas as pd

def nueva_sesion_ui(db):
    st.subheader("Nueva Sesión de Participación")
    
    # Selección de curso
    indices_cursos, nombres_cursos = db.obtener_lista_cursos()
    if not indices_cursos:
        st.warning("No hay cursos disponibles. Por favor, cree un curso primero.")
        return
    
    # Sidebar para configuración
    st.sidebar.subheader("Configuración de la Sesión")
    curso_seleccionado = st.sidebar.selectbox(
        "Selecciona el curso",
        nombres_cursos,
        key="nueva_sesion_curso"
    )
    indice_curso = indices_cursos[nombres_cursos.index(curso_seleccionado)]
    
    # Configuración de la sesión
    nombre_sesion = st.sidebar.text_input("Nombre de la Sesión", "Sesión 1")
    puntaje_maximo = st.sidebar.number_input("Puntaje Máximo", value=20, min_value=1)
    fecha_sesion = st.sidebar.date_input("Fecha", datetime.now())
    
    # Gestión de alumnos
    st.sidebar.subheader("Gestión de Alumnos")
    with st.sidebar.expander("Agregar Nuevo Alumno"):
        with st.form("nuevo_alumno"):
            nuevo_apellido = st.text_input("Apellido")
            nuevo_nombre = st.text_input("Nombre")
            submitted = st.form_submit_button("Agregar Alumno")
            
            if submitted and nuevo_apellido and nuevo_nombre:
                if db.agregar_alumno(indice_curso, nuevo_apellido, nuevo_nombre):
                    st.success("Alumno agregado exitosamente!")
                    st.rerun()
    
    # Tabla de alumnos y puntajes
    df_alumnos = db.leer_alumnos_curso(indice_curso)
    
    if not df_alumnos.empty:
        st.write("### Lista de Alumnos")
        df_editado = st.data_editor(
            df_alumnos,
            column_config={
                "Apellido": st.column_config.TextColumn("Apellido", disabled=True),
                "Nombre": st.column_config.TextColumn("Nombre", disabled=True),
                "Puntaje": st.column_config.NumberColumn(
                    "Puntaje",
                    min_value=0,
                    max_value=puntaje_maximo
                )
            },
            hide_index=True
        )
        
        if st.button("Guardar Sesión"):
            if nombre_sesion and fecha_sesion:
                sesion_id = db.guardar_sesion(
                    indice_curso,
                    nombre_sesion,
                    puntaje_maximo,
                    fecha_sesion,
                    df_editado
                )
                if sesion_id:
                    st.success("¡Sesión guardada exitosamente!")
    else:
        st.info("No hay alumnos registrados en este curso. Utilice el panel lateral para agregar alumnos.")