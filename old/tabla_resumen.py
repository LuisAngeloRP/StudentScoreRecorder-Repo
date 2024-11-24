import streamlit as st
import pandas as pd

def tabla_resumen_ui(db):
    st.subheader("Tabla de Resumen")
    
    # Selección de curso
    indices_cursos, nombres_cursos = db.obtener_lista_cursos()
    if not indices_cursos:
        st.warning("No hay cursos disponibles.")
        return
    
    curso_seleccionado = st.sidebar.selectbox(
        "Selecciona el curso",
        nombres_cursos,
        key="tabla_resumen_curso"
    )
    indice_curso = indices_cursos[nombres_cursos.index(curso_seleccionado)]
    
    # Obtener todas las sesiones del curso
    df_sesiones = db.obtener_sesiones_curso(indice_curso)
    if df_sesiones.empty:
        st.info(f"No hay sesiones registradas para el curso {curso_seleccionado}")
        return

    # Crear tabla de resumen
    try:
        # Obtener lista de alumnos
        df_alumnos = db.leer_alumnos_curso(indice_curso)
        alumnos = [f"{row['apellido']} {row['nombre']}" for _, row in df_alumnos.iterrows()]
        
        # Crear DataFrame para el resumen
        tabla_resumen = pd.DataFrame(index=alumnos)
        
        # Calcular totales y porcentajes
        total_puntos_posibles = 0
        for _, sesion in df_sesiones.iterrows():
            sesion_id = sesion['id']
            nombre_sesion = f"{sesion['nombre']} ({sesion['fecha']})"
            puntaje_maximo = sesion['puntaje_maximo']
            total_puntos_posibles += puntaje_maximo
            
            # Obtener puntajes de la sesión
            df_puntajes = db.obtener_puntajes_sesion(sesion_id)
            puntajes_dict = {f"{row['apellido']} {row['nombre']}": row['puntaje'] 
                            for _, row in df_puntajes.iterrows()}
            
            # Añadir columna a la tabla de resumen
            tabla_resumen[nombre_sesion] = tabla_resumen.index.map(puntajes_dict)
            
        # Calcular estadísticas
        tabla_resumen['Total Puntos'] = tabla_resumen.sum(axis=1)
        tabla_resumen['Porcentaje'] = (tabla_resumen['Total Puntos'] / total_puntos_posibles * 100).round(2)
        
        # Mostrar tabla de resumen
        st.write("### Resumen de Participaciones")
        st.dataframe(
            tabla_resumen,
            column_config={
                "Total Puntos": st.column_config.NumberColumn(
                    "Total Puntos",
                    format="%.1f"
                ),
                "Porcentaje": st.column_config.NumberColumn(
                    "Porcentaje (%)",
                    format="%.2f"
                )
            },
            height=400
        )
        
        # Mostrar estadísticas generales
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Promedio de Participación", 
                     f"{tabla_resumen['Porcentaje'].mean():.2f}%")
        with col2:
            st.metric("Participación más Alta", 
                     f"{tabla_resumen['Porcentaje'].max():.2f}%")
        with col3:
            st.metric("Participación más Baja", 
                     f"{tabla_resumen['Porcentaje'].min():.2f}%")
        
        # Opción para descargar el resumen
        csv = tabla_resumen.to_csv().encode('utf-8')
        st.download_button(
            label="Descargar Resumen (CSV)",
            data=csv,
            file_name=f'resumen_{curso_seleccionado}_{pd.Timestamp.now().strftime("%Y%m%d")}.csv',
            mime='text/csv'
        )
        
        # Visualización gráfica
        st.write("### Visualización de Participaciones")
        chart_type = st.radio(
            "Tipo de gráfico",
            ["Barras", "Líneas"],
            horizontal=True
        )
        
        if chart_type == "Barras":
            st.bar_chart(tabla_resumen['Porcentaje'])
        else:
            st.line_chart(tabla_resumen.drop(['Total Puntos', 'Porcentaje'], axis=1).T)
            
    except Exception as e:
        st.error(f"Error al generar el resumen: {str(e)}")