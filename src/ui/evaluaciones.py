import streamlit as st
from datetime import datetime
import pandas as pd
import plotly.express as px

def evaluaciones_ui(db):
    st.title("🎯 Evaluaciones")
    
    tab1, tab2 = st.tabs(["📝 Crear Evaluación", "📊 Ver Evaluaciones"])
    
    with tab1:
        crear_evaluacion(db)
    
    with tab2:
        ver_evaluaciones(db)

def calcular_nota(puntaje, puntaje_maximo, escala):
    """Calcula la nota en base a la escala definida"""
    if puntaje_maximo == 0:
        return 0
    return round((puntaje / puntaje_maximo) * escala, 2)

def crear_evaluacion(db):
    """Maneja la creación de una nueva evaluación"""
    st.markdown("### 📝 Crear Nueva Evaluación")
    
    # Selección de curso
    indices_cursos, nombres_cursos = db.obtener_lista_cursos()
    if not indices_cursos:
        st.warning("🚫 No hay cursos disponibles.")
        return
    
    curso_seleccionado = st.selectbox(
        "📚 Selecciona el curso",
        nombres_cursos,
        key="evaluacion_curso"
    )
    indice_curso = indices_cursos[nombres_cursos.index(curso_seleccionado)]
    
    # Configuración de la evaluación
    with st.container():
        col1, col2, col3 = st.columns([2,1,1])
        with col1:
            nombre_evaluacion = st.text_input("📋 Nombre de la Evaluación", "Evaluación 1")
        with col2:
            escala = st.number_input("📊 Escala", min_value=1, value=20)
        with col3:
            fecha_evaluacion = st.date_input("📅 Fecha", datetime.now())
    
    # Obtener sesiones disponibles
    df_sesiones = db.obtener_sesiones_curso(indice_curso)
    if df_sesiones.empty:
        st.warning("⚠️ No hay sesiones disponibles para crear una evaluación.")
        return
    
    # Selección de sesiones con mejor presentación
    st.markdown("### 📎 Seleccionar Sesiones")
    
    # Grid de sesiones para selección
    cols = st.columns(2)
    sesiones_seleccionadas = []
    
    for idx, sesion in df_sesiones.iterrows():
        with cols[idx % 2]:
            if st.checkbox(
                f"{sesion['nombre']} ({sesion['fecha']})",
                key=f"sesion_{sesion['id']}"
            ):
                st.markdown(f"""
                    <div style='
                        background-color: #f8f9fa;
                        padding: 8px;
                        border-radius: 6px;
                        font-size: 14px;
                        color: #0066cc;
                    '>
                        Puntaje máximo: {sesion['puntaje_maximo']} ✨
                    </div>
                """, unsafe_allow_html=True)
                sesiones_seleccionadas.append(sesion['id'])
    
    if len(sesiones_seleccionadas) > 0:
        if st.button("👀 Previsualizar Evaluación", use_container_width=True):
            try:
                evaluacion_temp_id = db.crear_evaluacion(
                    indice_curso,
                    "temp_eval",
                    escala,
                    sesiones_seleccionadas,
                    fecha_evaluacion
                )
                
                if evaluacion_temp_id is None:
                    st.error("Error al crear la evaluación temporal")
                    return
                
                # Obtener resultados
                df_resultados = db.obtener_resultados_evaluacion(evaluacion_temp_id)
                
                if df_resultados is None or df_resultados.empty:
                    st.warning("No hay resultados disponibles para mostrar")
                    return
                
                # Asegurar tipos de datos correctos
                df_resultados = df_resultados.fillna(0)
                df_resultados['Puntaje Total'] = df_resultados['Puntaje Total'].astype(float)
                df_resultados['Máximo Posible'] = df_resultados['Máximo Posible'].astype(float)
                df_resultados['Nota'] = df_resultados['Nota'].astype(float)
                
                # Contenedor para previsualización
                with st.container():
                    st.markdown("### 📊 Resultados Preliminares")
                    
                    # Estadísticas
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("📊 Promedio", f"{df_resultados['Nota'].mean():.2f}")
                    with col2:
                        st.metric("⬆️ Nota más alta", f"{df_resultados['Nota'].max():.2f}")
                    with col3:
                        st.metric("⬇️ Nota más baja", f"{df_resultados['Nota'].min():.2f}")
                    with col4:
                        st.metric("📝 Total Alumnos", len(df_resultados))
                    
                    # Tabla de resultados
                    st.dataframe(
                        df_resultados.sort_values('Nota', ascending=False),
                        column_config={
                            "Alumno": st.column_config.TextColumn(
                                "Alumno",
                                help="Nombre completo del alumno"
                            ),
                            "Puntaje Total": st.column_config.NumberColumn(
                                "Puntaje Total",
                                help="Suma de puntajes de todas las sesiones",
                                format="%.1f ✨"
                            ),
                            "Máximo Posible": st.column_config.NumberColumn(
                                "Máximo Posible",
                                help="Puntaje máximo alcanzable",
                                format="%.1f ✨"
                            ),
                            "Nota": st.column_config.NumberColumn(
                                "Nota",
                                help=f"Calificación en escala de {escala}",
                                format="%.2f"
                            )
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                    
                    # Gráfico de distribución
                    fig = px.histogram(
                        df_resultados, 
                        x='Nota', 
                        nbins=20,
                        title='Distribución de Notas',
                        labels={'Nota': f'Nota (escala {escala})', 'count': 'Cantidad de Alumnos'},
                        color_discrete_sequence=['#0066cc']
                    )
                    fig.update_layout(
                        showlegend=False,
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        margin=dict(t=50, l=0, r=0, b=0)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Botones de acción
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 Guardar Evaluación", use_container_width=True):
                            evaluacion_id = db.crear_evaluacion(
                                indice_curso,
                                nombre_evaluacion,
                                escala,
                                sesiones_seleccionadas,
                                fecha_evaluacion
                            )
                            
                            if evaluacion_id:
                                st.success("✅ ¡Evaluación creada exitosamente!")
                                st.balloons()
                    
                    with col2:
                        if not df_resultados.empty:
                            csv = df_resultados.to_csv().encode('utf-8')
                            st.download_button(
                                label="📥 Descargar Resultados (CSV)",
                                data=csv,
                                file_name=f'{nombre_evaluacion}_{datetime.now().strftime("%Y%m%d")}.csv',
                                mime='text/csv',
                                use_container_width=True
                            )
                            
            except Exception as e:
                st.error(f"Error al procesar la evaluación: {str(e)}")
                return
    else:
        st.info("ℹ️ Selecciona al menos una sesión para crear la evaluación")

def ver_evaluaciones(db):
    st.markdown("### 📊 Evaluaciones Existentes")
    
    indices_cursos, nombres_cursos = db.obtener_lista_cursos()
    if not indices_cursos:
        st.warning("🚫 No hay cursos disponibles.")
        return
    
    curso_seleccionado = st.selectbox(
        "📚 Selecciona el curso",
        nombres_cursos,
        key="ver_evaluaciones_curso"
    )
    indice_curso = indices_cursos[nombres_cursos.index(curso_seleccionado)]
    
    evaluaciones = db.obtener_evaluaciones_curso(indice_curso)
    if not evaluaciones:
        st.info("📝 No hay evaluaciones registradas para este curso.")
        return
    
    evaluacion_seleccionada = st.selectbox(
        "Selecciona una evaluación",
        [f"{eval['nombre']} ({eval['fecha']})" for eval in evaluaciones]
    )
    
    if evaluacion_seleccionada:
        idx = [f"{eval['nombre']} ({eval['fecha']})" for eval in evaluaciones].index(evaluacion_seleccionada)
        evaluacion = evaluaciones[idx]
        
        st.markdown(f"""
            <div style='
                background-color: white;
                padding: 15px;
                border-radius: 10px;
                margin: 15px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            '>
                <h3 style='margin: 0;'>{evaluacion['nombre']}</h3>
                <p style='margin: 5px 0;'>📅 Fecha: {evaluacion['fecha']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Mostrar sesiones incluidas en una grid
        with st.expander("📎 Sesiones incluidas"):
            cols = st.columns(2)
            for idx, sesion in enumerate(evaluacion['sesiones']):
                with cols[idx % 2]:
                    st.markdown(f"""
                        <div style='
                            background-color: #f8f9fa;
                            padding: 10px;
                            border-radius: 8px;
                            margin: 5px 0;
                        '>
                            <div style='font-weight: bold;'>{sesion['nombre']}</div>
                            <div style='color: #666;'>📅 {sesion['fecha']}</div>
                            <div style='color: #0066cc;'>✨ Máximo: {sesion['puntaje_maximo']} puntos</div>
                        </div>
                    """, unsafe_allow_html=True)
        
        # Obtener y mostrar resultados
        df_resultados = db.obtener_resultados_evaluacion(evaluacion['id'])
        if df_resultados is not None:
            # Métricas en cards
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Promedio", f"{df_resultados['Nota'].mean():.2f}")
            with col2:
                st.metric("⬆️ Nota más alta", f"{df_resultados['Nota'].max():.2f}")
            with col3:
                st.metric("⬇️ Nota más baja", f"{df_resultados['Nota'].min():.2f}")
            with col4:
                st.metric("📝 Total Alumnos", len(df_resultados))
            
            # Tabla mejorada
            st.dataframe(
                df_resultados.sort_values('Nota', ascending=False),
                column_config={
                    "Alumno": st.column_config.TextColumn(
                        "Alumno",
                        help="Nombre completo del alumno"
                    ),
                    "Puntaje Total": st.column_config.NumberColumn(
                        "Puntaje Total",
                        help="Suma de puntajes de todas las sesiones",
                        format="%.1f ✨"
                    ),
                    "Máximo Posible": st.column_config.NumberColumn(
                        "Máximo Posible",
                        help="Puntaje máximo alcanzable",
                        format="%.1f ✨"
                    ),
                    "Nota": st.column_config.NumberColumn(
                        "Nota",
                        help=f"Calificación final",
                        format="%.2f"
                    )
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Gráfico mejorado
            st.markdown("### 📊 Distribución de Notas")
            fig = px.histogram(
                df_resultados, 
                x='Nota', 
                nbins=20,
                title='Distribución de Notas',
                labels={'Nota': 'Calificación', 'count': 'Cantidad de Alumnos'},
                color_discrete_sequence=['#0066cc']
            )
            fig.update_layout(
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(t=50, l=0, r=0, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Botones de acción al final
            col1, col2 = st.columns(2)
            with col1:
                csv = df_resultados.to_csv().encode('utf-8')
                st.download_button(
                    label="📥 Descargar Resultados (CSV)",
                    data=csv,
                    file_name=f'{evaluacion["nombre"]}_{datetime.now().strftime("%Y%m%d")}.csv',
                    mime='text/csv',
                    use_container_width=True
                )
            
            with col2:
                if st.button("🗑️ Eliminar Evaluación", type="primary", use_container_width=True):
                    if db.eliminar_evaluacion(evaluacion['id']):
                        st.success("✅ Evaluación eliminada exitosamente")
                        st.rerun()