import pandas as pd
import streamlit as st

def gestionar_cursos_ui(db):
    st.subheader("Gestionar Cursos")
    
    # Formulario para crear nuevo curso
    with st.form("nuevo_curso"):
        st.write("### Crear Nuevo Curso")
        nombre = st.text_input("Nombre del Curso")
        codigo = st.text_input("Código del Curso")
        submitted = st.form_submit_button("Crear Curso")
        
        if submitted and nombre and codigo:
            if db.crear_curso(nombre, codigo):
                st.success(f"Curso '{nombre}' creado exitosamente!")
                st.rerun()
    
    # Mostrar cursos existentes
    st.write("### Cursos Existentes")
    codigos, nombres = db.obtener_lista_cursos()
    if codigos and nombres:
        df = pd.DataFrame({
            'Código': codigos,
            'Nombre': nombres
        })
        st.dataframe(df)
    else:
        st.info("No hay cursos registrados.")