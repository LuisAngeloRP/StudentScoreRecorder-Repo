import streamlit as st
from datetime import datetime
import pandas as pd
import plotly.express as px

def calcular_nota(puntaje, puntaje_maximo, escala):
    """Calcula la nota en base a la escala definida"""
    if puntaje_maximo == 0:
        return 0
    return round((puntaje / puntaje_maximo) * escala, 2)

def evaluaciones_ui(db):
    st.subheader("Evaluaciones")
    
    tab1, tab2 = st.tabs(["Crear Evaluación", "Ver Evaluaciones"])
    
    with tab1:
        crear_evaluacion(db)
    
    with tab2:
        ver_evaluaciones(db)

def crear_evaluacion(db):
    st.write("### Crear Nueva Evaluación")
    
    # Selección de curso
    indices_cursos, nombres_cursos = db.obtener_lista_cursos()
    if not indices_cursos:
        st.warning("No hay cursos disponibles.")
        return
    
    curso_seleccionado = st.selectbox(
        "Selecciona el curso",
        nombres_cursos,
        key="evaluacion_curso"
    )
    indice_curso = indices_cursos[nombres_cursos.index(curso_seleccionado)]
    
    # Configuración de la evaluación
    col1, col2 = st.columns(2)
    with col1:
        nombre_evaluacion = st.text_input("Nombre de la Evaluación", "Evaluación 1")
        escala = st.number_input("Escala de Calificación", min_value=1, value=20)
    
    with col2:
        fecha_evaluacion = st.date_input("Fecha", datetime.now())
    
    # Obtener sesiones disponibles
    df_sesiones = db.obtener_sesiones_curso(indice_curso)
    if df_sesiones.empty:
        st.warning("No hay sesiones disponibles para crear una evaluación.")
        return
    
    # Selección de sesiones
    st.write("### Seleccionar Sesiones")
    sesiones_seleccionadas = []
    for _, sesion in df_sesiones.iterrows():
        if st.checkbox(
            f"{sesion['nombre']} ({sesion['fecha']}) - Máximo: {sesion['puntaje_maximo']} puntos",
            key=f"sesion_{sesion['id']}"
        ):
            sesiones_seleccionadas.append(sesion['id'])
    
    if len(sesiones_seleccionadas) > 0:
        st.write("### Previsualización")
        
        # Obtener y mostrar resultados preliminares
        df_resultados = db.obtener_resultados_evaluacion(
            db.crear_evaluacion(
                indice_curso,
                "temp_eval",
                escala,
                sesiones_seleccionadas,
                fecha_evaluacion
            )
        )
        
        if df_resultados is not None:
            st.dataframe(df_resultados)
            
            # Estadísticas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Promedio", f"{df_resultados['Nota'].mean():.2f}")
            with col2:
                st.metric("Nota más alta", f"{df_resultados['Nota'].max():.2f}")
            with col3:
                st.metric("Nota más baja", f"{df_resultados['Nota'].min():.2f}")
            
            if st.button("Guardar Evaluación"):
                evaluacion_id = db.crear_evaluacion(
                    indice_curso,
                    nombre_evaluacion,
                    escala,
                    sesiones_seleccionadas,
                    fecha_evaluacion
                )
                
                if evaluacion_id:
                    st.success("¡Evaluación creada exitosamente!")
                    # Opción para descargar
                    csv = df_resultados.to_csv().encode('utf-8')
                    st.download_button(
                        label="Descargar Resultados (CSV)",
                        data=csv,
                        file_name=f'{nombre_evaluacion}_{datetime.now().strftime("%Y%m%d")}.csv',
                        mime='text/csv'
                    )

def ver_evaluaciones(db):
    st.write("### Evaluaciones Existentes")
    
    # Selección de curso
    indices_cursos, nombres_cursos = db.obtener_lista_cursos()
    if not indices_cursos:
        st.warning("No hay cursos disponibles.")
        return
    
    curso_seleccionado = st.selectbox(
        "Selecciona el curso",
        nombres_cursos,
        key="ver_evaluaciones_curso"
    )
    indice_curso = indices_cursos[nombres_cursos.index(curso_seleccionado)]
    
    # Obtener evaluaciones
    evaluaciones = db.obtener_evaluaciones_curso(indice_curso)
    if not evaluaciones:
        st.info("No hay evaluaciones registradas para este curso.")
        return
    
    # Mostrar lista de evaluaciones
    evaluacion_seleccionada = st.selectbox(
        "Selecciona una evaluación",
        [f"{eval['nombre']} ({eval['fecha']})" for eval in evaluaciones]
    )
    
    if evaluacion_seleccionada:
        idx = [f"{eval['nombre']} ({eval['fecha']})" for eval in evaluaciones].index(evaluacion_seleccionada)
        evaluacion = evaluaciones[idx]
        
        st.write(f"### Detalles de {evaluacion['nombre']}")
        
        # Mostrar sesiones incluidas
        with st.expander("Sesiones incluidas"):
            for sesion in evaluacion['sesiones']:
                st.write(f"- {sesion['nombre']} ({sesion['fecha']}) - Máximo: {sesion['puntaje_maximo']} puntos")
        
        # Obtener y mostrar resultados
        df_resultados = db.obtener_resultados_evaluacion(evaluacion['id'])
        if df_resultados is not None:
            st.dataframe(df_resultados)
            
            # Estadísticas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Promedio", f"{df_resultados['Nota'].mean():.2f}")
            with col2:
                st.metric("Nota más alta", f"{df_resultados['Nota'].max():.2f}")
            with col3:
                st.metric("Nota más baja", f"{df_resultados['Nota'].min():.2f}")
            
            # Gráfico de distribución
            st.write("### Distribución de Notas")
            fig = px.histogram(df_resultados, x='Nota', nbins=20)
            st.plotly_chart(fig)
            
            # Opción para descargar
            csv = df_resultados.to_csv().encode('utf-8')
            st.download_button(
                label="Descargar Resultados (CSV)",
                data=csv,
                file_name=f'{evaluacion["nombre"]}_{datetime.now().strftime("%Y%m%d")}.csv',
                mime='text/csv'
            )
            
            # Opción para eliminar
            if st.button("Eliminar Evaluación", type="primary"):
                if db.eliminar_evaluacion(evaluacion['id']):
                    st.success("Evaluación eliminada exitosamente")
                    st.rerun()