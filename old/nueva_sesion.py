import streamlit as st
from datetime import datetime
import pandas as pd

def nueva_sesion_ui(db):
    st.subheader("Nueva Sesión de Participación")
    
    # Estilos CSS personalizados
    st.markdown("""
        <style>
        .student-row {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: flex;
            align-items: center;
        }
        
        .student-name {
            font-size: 16px;
            color: #2c3e50;
            flex-grow: 1;
            padding: 8px 0;
        }
        
        .score-display {
            font-size: 24px;
            font-weight: bold;
            color: #0066cc;
            text-align: center;
            min-width: 60px;
            padding: 5px 15px;
            margin: 0 10px;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .controls-container {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-left: auto;
        }
        
        .stButton button {
            width: 40px !important;
            height: 40px !important;
            border-radius: 20px !important;
            padding: 0px !important;
            line-height: 40px !important;
            font-size: 20px !important;
            font-weight: bold !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Selección de curso
    indices_cursos, nombres_cursos = db.obtener_lista_cursos()
    if not indices_cursos:
        st.warning("No hay cursos disponibles. Por favor, cree un curso primero.")
        return
    
    # Sidebar para configuración
    with st.sidebar:
        st.markdown("### ⚙️ Configuración de la Sesión")
        curso_seleccionado = st.selectbox(
            "📚 Selecciona el curso",
            nombres_cursos,
            key="nueva_sesion_curso"
        )
        indice_curso = indices_cursos[nombres_cursos.index(curso_seleccionado)]
        
        nombre_sesion = st.text_input("📝 Nombre de la Sesión", "Sesión 1")
        puntaje_maximo = st.number_input("🎯 Puntaje Máximo", value=20, min_value=1)
        fecha_sesion = st.date_input("📅 Fecha", datetime.now())
        
        st.markdown("### 👥 Gestión de Alumnos")
        with st.expander("➕ Agregar Nuevo Alumno"):
            with st.form("nuevo_alumno"):
                nuevo_apellido = st.text_input("Apellido")
                nuevo_nombre = st.text_input("Nombre")
                submitted = st.form_submit_button("Agregar Alumno")
                
                if submitted and nuevo_apellido and nuevo_nombre:
                    if db.agregar_alumno(indice_curso, nuevo_apellido, nuevo_nombre):
                        st.success("Alumno agregado exitosamente!")
                        st.rerun()
    
    # Obtener datos de alumnos
    df_alumnos = db.leer_alumnos_curso(indice_curso)
    
    if not df_alumnos.empty:
        # Inicializar el estado de los puntajes
        if 'puntajes' not in st.session_state:
            st.session_state.puntajes = {
                idx: 0 for idx in range(len(df_alumnos))
            }
        
        # Selector de vista estilizado
        vista_seleccionada = st.radio(
            "📊 Seleccionar vista",
            ["Vista de Botones", "Vista de Tabla"],
            horizontal=True,
            key="selector_vista"
        )
        
        if vista_seleccionada == "Vista de Tabla":
            mostrar_vista_tabla(db, df_alumnos, puntaje_maximo, indice_curso)
        else:
            mostrar_vista_botones(db, df_alumnos, puntaje_maximo, indice_curso)
        
        # Botón de guardar sesión
        if st.button("💾 Guardar Sesión", use_container_width=True):
            if nombre_sesion and fecha_sesion:
                df_alumnos['Puntaje'] = [st.session_state.puntajes[i] for i in range(len(df_alumnos))]
                sesion_id = db.guardar_sesion(
                    indice_curso,
                    nombre_sesion,
                    puntaje_maximo,
                    fecha_sesion,
                    df_alumnos
                )
                if sesion_id:
                    st.success("¡Sesión guardada exitosamente! 🎉")
    else:
        st.info("📝 No hay alumnos registrados en este curso. Utilice el panel lateral para agregar alumnos.")

def mostrar_vista_tabla(db, df_alumnos: pd.DataFrame, puntaje_maximo: int, codigo_curso: str):
    """Vista de tabla editable con sincronización en tiempo real"""
    st.markdown("### 📋 Lista de Alumnos")
    df_editado = st.data_editor(
        df_alumnos,
        column_config={
            "Apellido": st.column_config.TextColumn(
                "Apellido",
                disabled=True,
                width="medium"
            ),
            "Nombre": st.column_config.TextColumn(
                "Nombre",
                disabled=True,
                width="medium"
            ),
            "Puntaje": st.column_config.NumberColumn(
                "Puntaje",
                min_value=0,
                max_value=puntaje_maximo,
                default=0,
                width="small",
                format="%d ✨"
            )
        },
        hide_index=True,
        key="tabla_puntajes"
    )
    
    # Actualizar puntajes y sincronizar con Supabase
    for i, row in df_editado.iterrows():
        nuevo_puntaje = row['Puntaje'] if not pd.isna(row['Puntaje']) else 0
        if st.session_state.puntajes[i] != nuevo_puntaje:
            # Actualizar en Supabase
            actualizado = db.actualizar_puntaje_alumno(
                codigo_curso,
                row['Apellido'],
                row['Nombre'],
                nuevo_puntaje
            )
            if actualizado:
                st.session_state.puntajes[i] = nuevo_puntaje
            else:
                st.error(f"Error al actualizar puntaje de {row['Apellido']}, {row['Nombre']}")

def mostrar_vista_botones(db, df_alumnos: pd.DataFrame, puntaje_maximo: int, codigo_curso: str):
    """Vista de botones con sincronización en tiempo real"""
    st.markdown("### 🎯 Control de Puntajes")
    
    for i, row in df_alumnos.iterrows():
        st.markdown(f"""
            <div class="student-row">
                <div class="student-name">{row['Apellido']}, {row['Nombre']}</div>
                <div class="controls-container">
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("➖", key=f"dec_{i}", help="Disminuir puntaje"):
                if st.session_state.puntajes[i] > 0:
                    nuevo_puntaje = st.session_state.puntajes[i] - 1
                    actualizado = db.actualizar_puntaje_alumno(
                        codigo_curso,
                        row['Apellido'],
                        row['Nombre'],
                        nuevo_puntaje
                    )
                    if actualizado:
                        st.session_state.puntajes[i] = nuevo_puntaje
                        st.rerun()
        
        with col2:
            st.markdown(f"""
                <div class="score-display">
                    {st.session_state.puntajes[i]}
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            if st.button("➕", key=f"inc_{i}", help="Aumentar puntaje"):
                if st.session_state.puntajes[i] < puntaje_maximo:
                    nuevo_puntaje = st.session_state.puntajes[i] + 1
                    actualizado = db.actualizar_puntaje_alumno(
                        codigo_curso,
                        row['Apellido'],
                        row['Nombre'],
                        nuevo_puntaje
                    )
                    if actualizado:
                        st.session_state.puntajes[i] = nuevo_puntaje
                        st.rerun()
        
        st.markdown("""
                </div>
            </div>
        """, unsafe_allow_html=True)