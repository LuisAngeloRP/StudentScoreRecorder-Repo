import streamlit as st
from ..utils.validators import validar_puntaje_maximo

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
        sesion_id = df_sesiones.iloc[sesion_index]['id']
        puntaje_maximo = df_sesiones.iloc[sesion_index]['puntaje_maximo']
        
        df_puntajes = db.obtener_puntajes_sesion(sesion_id)
        
        st.write(f"### Puntajes de {sesion_seleccionada}")
        df_editado = st.data_editor(
            df_puntajes,
            column_config={
                "apellido": st.column_config.TextColumn("Apellido", disabled=True),
                "nombre": st.column_config.TextColumn("Nombre", disabled=True),
                "puntaje": st.column_config.NumberColumn(
                    "Puntaje",
                    min_value=0,
                    max_value=puntaje_maximo
                )
            },
            hide_index=True
        )
        
        if st.button("Guardar Cambios"):
            if validar_puntaje_maximo(df_editado, puntaje_maximo):
                db.actualizar_puntajes_sesion(sesion_id, df_editado)
                st.success("Cambios guardados exitosamente!")