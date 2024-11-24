import streamlit as st
import pandas as pd
from ..src.utils.validators import validar_puntaje_maximo

def mostrar_sesiones_guardadas(db, indice_curso, curso_seleccionado):
    """Muestra el listado de sesiones guardadas con mejor diseño"""
    df_sesiones = db.obtener_sesiones_curso(indice_curso)
    
    if df_sesiones.empty:
        st.info(f"No hay sesiones guardadas para el curso {curso_seleccionado}")
        return
    
    # Ordenar sesiones por fecha descendente
    df_sesiones = df_sesiones.sort_values('fecha', ascending=False)
    
    # Crear grid de tarjetas de sesiones
    col1, col2 = st.columns(2)
    for idx, sesion in df_sesiones.iterrows():
        with col1 if idx % 2 == 0 else col2:
            with st.container():
                st.markdown(f"""
                    <div style='
                        background-color: white;
                        padding: 20px;
                        border-radius: 10px;
                        margin-bottom: 20px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        cursor: pointer;
                    '>
                        <h3 style='margin: 0;'>{sesion['nombre']}</h3>
                        <p style='color: #666; margin: 5px 0;'>Fecha: {sesion['fecha']}</p>
                        <p style='margin: 5px 0;'>Puntaje máximo: {sesion['puntaje_maximo']} ✨</p>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button("Ver Detalles", key=f"ver_sesion_{sesion['id']}", use_container_width=True):
                    st.session_state.sesion_seleccionada = sesion['id']
                    st.rerun()

def sesiones_guardadas_tab(db):
    st.subheader("Sesiones Guardadas")
    
    # Selección de curso
    indices_cursos, nombres_cursos = db.obtener_lista_cursos()
    if not indices_cursos:
        st.warning("No hay cursos disponibles.")
        return
    
    curso_seleccionado = st.sidebar.selectbox(
        "Selecciona el curso",
        nombres_cursos,
        key="sesiones_guardadas_curso"
    )
    indice_curso = indices_cursos[nombres_cursos.index(curso_seleccionado)]
    
    # Obtener sesiones del curso
    df_sesiones = db.obtener_sesiones_curso(indice_curso)
    if df_sesiones.empty:
        st.info(f"No hay sesiones guardadas para el curso {curso_seleccionado}")
        return
    
    # Convertir columnas numéricas a tipos Python nativos
    df_sesiones = df_sesiones.astype({
        'id': int,
        'puntaje_maximo': int
    })
    
    # Selección de sesión
    sesiones_list = [
        f"{row['nombre']} ({row['fecha']})" 
        for _, row in df_sesiones.iterrows()
    ]
    
    sesion_seleccionada = st.sidebar.selectbox(
        "Selecciona una sesión",
        sesiones_list
    )
    
    if sesion_seleccionada:
        sesion_index = sesiones_list.index(sesion_seleccionada)
        sesion_id = int(df_sesiones.iloc[sesion_index]['id'])  # Convertir a int nativo
        puntaje_maximo = int(df_sesiones.iloc[sesion_index]['puntaje_maximo'])  # Convertir a int nativo
        
        df_puntajes = db.obtener_puntajes_sesion(sesion_id)
        
        # Asegurarse de que el puntaje sea int
        if 'puntaje' in df_puntajes.columns:
            df_puntajes['puntaje'] = df_puntajes['puntaje'].astype(int)
        
        st.write(f"### Puntajes de {sesion_seleccionada}")
        
        # Crear una copia del DataFrame para edición
        df_editado = st.data_editor(
            df_puntajes,
            column_config={
                "apellido": st.column_config.TextColumn(
                    "Apellido",
                    disabled=True,
                    required=True
                ),
                "nombre": st.column_config.TextColumn(
                    "Nombre",
                    disabled=True,
                    required=True
                ),
                "puntaje": st.column_config.NumberColumn(
                    "Puntaje",
                    min_value=0,
                    max_value=puntaje_maximo,
                    step=1,
                    format="%d"
                )
            },
            hide_index=True,
            key=f"editor_{sesion_id}"
        )
        
        # Convertir DataFrame a tipos nativos antes de validar
        df_editado = df_editado.copy()
        df_editado['puntaje'] = df_editado['puntaje'].astype(int)
        
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("Guardar Cambios", type="primary"):
                if validar_puntaje_maximo(df_editado, puntaje_maximo):
                    # Asegurarse de que los datos están en el formato correcto
                    datos_actualizacion = df_editado.astype({
                        'apellido': str,
                        'nombre': str,
                        'puntaje': int
                    })
                    
                    if db.actualizar_puntajes_sesion(sesion_id, datos_actualizacion):
                        st.success("✅ Cambios guardados exitosamente!")
                    else:
                        st.error("❌ Error al guardar los cambios")
        
        # Mostrar estadísticas
        with st.expander("Ver estadísticas de la sesión"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Promedio",
                    f"{df_editado['puntaje'].mean():.1f}",
                    help="Promedio de puntajes"
                )
            with col2:
                st.metric(
                    "Puntaje más alto",
                    int(df_editado['puntaje'].max()),
                    help="Puntaje máximo alcanzado"
                )
            with col3:
                st.metric(
                    "Puntaje más bajo",
                    int(df_editado['puntaje'].min()),
                    help="Puntaje mínimo alcanzado"
                )
            
            # Mostrar distribución de puntajes
            st.write("### Distribución de puntajes")
            hist_data = df_editado['puntaje'].value_counts().sort_index()
            st.bar_chart(hist_data)