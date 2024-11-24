import streamlit as st
import pandas as pd

def sesion_actual_ui(db):
    """Interfaz para la sesión actual"""
    st.title("Sesión Actual")
    
    # Configuración inicial
    indices_cursos, nombres_cursos = db.obtener_lista_cursos()
    if not indices_cursos:
        st.warning("No hay cursos disponibles. Por favor, cree un curso primero.")
        return
    
    # Selector de curso
    curso_seleccionado = st.selectbox(
        "📚 Selecciona el curso",
        nombres_cursos,
        key="sesion_actual_curso"
    )
    indice_curso = indices_cursos[nombres_cursos.index(curso_seleccionado)]
    
    # Obtener lista de sesiones disponibles
    df_sesiones = db.obtener_sesiones_curso(indice_curso)
    
    if df_sesiones.empty:
        st.info("No hay sesiones disponibles. Crea una nueva sesión en la pestaña 'Sesiones'.")
        return
    
    # Selector de sesión
    sesiones_list = [f"{row['nombre']} ({row['fecha']})" for _, row in df_sesiones.iterrows()]
    sesion_seleccionada = st.selectbox(
        "Selecciona la sesión",
        sesiones_list,
        key="selector_sesion_actual"
    )
    
    if sesion_seleccionada:
        idx = sesiones_list.index(sesion_seleccionada)
        sesion = df_sesiones.iloc[idx]
        
        # Mostrar información de la sesión
        st.markdown(f"""
            <div style='
                background-color: white;
                padding: 15px;
                border-radius: 10px;
                margin: 10px 0 20px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            '>
                <h3 style='margin: 0;'>{sesion['nombre']}</h3>
                <p style='margin: 5px 0;'>Puntaje máximo: {sesion['puntaje_maximo']} ✨</p>
            </div>
        """, unsafe_allow_html=True)
        
        vista = st.radio(
            "Tipo de vista",
            ["Botones", "Tabla"],
            horizontal=True,
            key="tipo_vista_actual"
        )
        
        # Obtener y preparar datos de puntajes
        df_puntajes = db.obtener_puntajes_sesion(sesion['id'])
        if df_puntajes.empty:
            df_puntajes = db.leer_alumnos_curso(indice_curso)
            df_puntajes['Puntaje'] = 0
        
        # Ordenar alfabéticamente por apellido y nombre
        df_puntajes = df_puntajes.sort_values(['Apellido', 'Nombre']).reset_index(drop=True)
        
        if vista == "Botones":
            mostrar_vista_botones_edicion(db, df_puntajes, sesion)
        else:
            mostrar_vista_tabla_edicion(db, df_puntajes, sesion)

def mostrar_vista_botones_edicion(db, df_puntajes, sesion):
    """Vista de botones simplificada y funcional en una columna"""
    # CSS personalizado para los botones
    st.markdown("""
        <style>
        .stButton>button {
            width: 40px;
            height: 40px;
            padding: 0px;
        }
        .numero-alumno {
            background-color: #e9ecef;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 12px;
            color: #495057;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Contenedor principal
    with st.container():
        for idx, alumno in df_puntajes.iterrows():
            with st.container():
                # Contenedor para cada alumno con número de índice
                st.markdown(f"""
                    <div style='
                        background-color: #f8f9fa;
                        padding: 12px;
                        border-radius: 8px;
                        margin: 5px 0;
                        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                    '>
                        <div style='
                            display: flex;
                            align-items: center;
                            margin-bottom: 8px;
                        '>
                            <span class='numero-alumno'>{idx + 1}</span>
                            <span style='
                                font-size: 15px;
                                color: #2c3e50;
                                margin-left: 10px;
                            '>
                                {alumno['Apellido']}, {alumno['Nombre']}
                            </span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Botones y puntaje en una línea
                col1, col2, col3 = st.columns([1,2,1])
                
                with col1:
                    minus_button = """➖"""
                    if st.button(minus_button, key=f"dec_{alumno['Apellido']}_{alumno['Nombre']}", 
                               use_container_width=True):
                        nuevo_puntaje = max(0, alumno['Puntaje'] - 1)
                        db.actualizar_puntaje_en_sesion(
                            sesion['id'],
                            alumno['Apellido'],
                            alumno['Nombre'],
                            nuevo_puntaje
                        )
                        st.rerun()
                
                with col2:
                    st.markdown(f"""
                        <div style='
                            font-size: 20px;
                            font-weight: bold;
                            color: #0066cc;
                            text-align: center;
                            background-color: white;
                            padding: 4px 10px;
                            border-radius: 6px;
                            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                        '>
                            {alumno['Puntaje']} / {sesion['puntaje_maximo']}
                        </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    plus_button = """➕"""
                    if st.button(plus_button, key=f"inc_{alumno['Apellido']}_{alumno['Nombre']}", 
                               use_container_width=True):
                        nuevo_puntaje = min(sesion['puntaje_maximo'], alumno['Puntaje'] + 1)
                        db.actualizar_puntaje_en_sesion(
                            sesion['id'],
                            alumno['Apellido'],
                            alumno['Nombre'],
                            nuevo_puntaje
                        )
                        st.rerun()

def mostrar_vista_tabla_edicion(db, df_puntajes, sesion):
    """Vista de tabla para edición de puntajes"""
    # Agregar columna de índice
    df_puntajes = df_puntajes.reset_index()
    df_puntajes['index'] = df_puntajes['index'] + 1
    df_puntajes = df_puntajes.rename(columns={'index': 'N°'})
    
    df_editado = st.data_editor(
        df_puntajes,
        column_config={
            "N°": st.column_config.NumberColumn(
                "N°",
                disabled=True,
                format="%d"
            ),
            "Apellido": st.column_config.TextColumn(
                "Apellido",
                disabled=True
            ),
            "Nombre": st.column_config.TextColumn(
                "Nombre",
                disabled=True
            ),
            "Puntaje": st.column_config.NumberColumn(
                "Puntaje",
                min_value=0,
                max_value=sesion['puntaje_maximo'],
                step=1,
                format="%d ✨"
            )
        },
        hide_index=True,
        key=f"editor_sesion_{sesion['id']}"
    )
    
    # Actualizar puntajes
    for _, row in df_editado.iterrows():
        db.actualizar_puntaje_en_sesion(
            sesion['id'],
            row['Apellido'],
            row['Nombre'],
            row['Puntaje']
        )