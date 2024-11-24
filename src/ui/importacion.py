import streamlit as st
import pandas as pd
import io
from datetime import datetime

def importacion_ui(db):
    st.title("Importación de Cursos y Alumnos")
    
    tab1, tab2 = st.tabs(["Importar Datos", "Descargar Plantillas"])
    
    with tab1:
        importar_datos(db)
    
    with tab2:
        descargar_plantillas()

def importar_datos(db):
    st.header("Importar Nuevo Curso")
    
    # Sección de información del curso
    with st.form("info_curso"):
        st.subheader("1. Información del Curso")
        col1, col2 = st.columns(2)
        with col1:
            nombre_curso = st.text_input("Nombre del Curso", 
                                       placeholder="Ej: Matemáticas 2024-1")
        with col2:
            codigo_curso = st.text_input("Código del Curso", 
                                       placeholder="Ej: MAT101")
        
        submitted_curso = st.form_submit_button("Validar Información del Curso")
        
        if submitted_curso:
            if not nombre_curso or not codigo_curso:
                st.error("Por favor, complete todos los campos del curso.")
                return
            
            # Verificar si el código ya existe
            codigos_existentes, _ = db.obtener_lista_cursos()
            if codigo_curso in codigos_existentes:
                st.error("Este código de curso ya existe. Por favor, use otro código.")
                return
            
            st.success("Información del curso válida. Proceda a importar la lista de alumnos.")
            st.session_state.curso_validado = True
            st.session_state.nombre_curso = nombre_curso
            st.session_state.codigo_curso = codigo_curso

    # Sección de importación de alumnos
    if 'curso_validado' in st.session_state and st.session_state.curso_validado:
        st.subheader("2. Lista de Alumnos")
        
        metodo_importacion = st.radio(
            "Seleccione el método de importación:",
            ["Subir archivo Excel/CSV", "Copiar y pegar datos", "Ingresar manualmente"],
            horizontal=True
        )
        
        if metodo_importacion == "Subir archivo Excel/CSV":
            importar_desde_archivo(db)
        elif metodo_importacion == "Copiar y pegar datos":
            importar_desde_texto(db)
        else:
            importar_manual(db)

def importar_desde_archivo(db):
    uploaded_file = st.file_uploader(
        "Seleccione el archivo de alumnos (Excel o CSV)", 
        type=['xlsx', 'csv']
    )
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file, engine='openpyxl')
            
            if validar_formato_alumnos(df):
                mostrar_preview_y_guardar(db, df)
            
        except Exception as e:
            st.error(f"Error al leer el archivo: {str(e)}")

def importar_desde_texto(db):
    st.info("""
    Copie y pegue sus datos en el siguiente formato:
    ```
    Apellido,Nombre
    García,Juan
    López,María
    ...
    ```
    """)
    
    texto_datos = st.text_area(
        "Pegue los datos aquí",
        height=200,
        placeholder="Apellido,Nombre\nGarcía,Juan\nLópez,María"
    )
    
    if st.button("Procesar datos"):
        if texto_datos:
            try:
                # Convertir texto a DataFrame
                df = pd.DataFrame([
                    line.split(',') for line in texto_datos.strip().split('\n')
                ])
                if len(df.columns) >= 2:
                    df.columns = df.iloc[0]
                    df = df[1:]
                    if validar_formato_alumnos(df):
                        mostrar_preview_y_guardar(db, df)
                else:
                    st.error("Formato incorrecto. Asegúrese de separar los datos con comas.")
            except Exception as e:
                st.error(f"Error al procesar los datos: {str(e)}")

def importar_manual(db):
    if 'alumnos_manual' not in st.session_state:
        st.session_state.alumnos_manual = pd.DataFrame(columns=['Apellido', 'Nombre'])
    
    with st.form("agregar_alumno"):
        col1, col2 = st.columns(2)
        with col1:
            apellido = st.text_input("Apellido")
        with col2:
            nombre = st.text_input("Nombre")
        
        if st.form_submit_button("Agregar Alumno"):
            if apellido and nombre:
                nuevo_alumno = pd.DataFrame([[apellido, nombre]], columns=['Apellido', 'Nombre'])
                st.session_state.alumnos_manual = pd.concat([
                    st.session_state.alumnos_manual, 
                    nuevo_alumno
                ]).reset_index(drop=True)
                st.success("Alumno agregado.")
    
    if not st.session_state.alumnos_manual.empty:
        st.write("### Alumnos ingresados:")
        st.dataframe(st.session_state.alumnos_manual)
        
        if st.button("Guardar Lista de Alumnos"):
            mostrar_preview_y_guardar(db, st.session_state.alumnos_manual)

def validar_formato_alumnos(df):
    """Valida el formato del DataFrame de alumnos"""
    columnas_requeridas = ['Apellido', 'Nombre']
    
    # Verificar columnas
    if not all(col in df.columns for col in columnas_requeridas):
        st.error(f"El archivo debe contener las columnas: {', '.join(columnas_requeridas)}")
        return False
    
    # Verificar datos vacíos
    if df['Apellido'].isna().any() or df['Nombre'].isna().any():
        st.error("Existen datos vacíos en la lista de alumnos")
        return False
    
    # Verificar duplicados
    duplicados = df.duplicated(subset=['Apellido', 'Nombre'], keep=False)
    if duplicados.any():
        st.error("Existen alumnos duplicados en la lista:")
        st.dataframe(df[duplicados])
        return False
    
    return True

def mostrar_preview_y_guardar(db, df):
    st.write("### Vista previa de los datos:")
    st.dataframe(df)
    
    # Verificación inicial del estado
    if 'nombre_curso' not in st.session_state or 'codigo_curso' not in st.session_state:
        st.error("Error: Información del curso no encontrada. Complete la información del curso primero.")
        return

    # Contenedor para mensajes de estado
    estado_container = st.empty()
    
    # Inicializar el estado del proceso si no existe
    if 'proceso_estado' not in st.session_state:
        st.session_state.proceso_estado = {
            'iniciado': False,
            'curso_creado': False,
            'alumnos_agregados': 0,
            'completado': False,
            'errores': []
        }

    # Botón para iniciar el proceso con manejo de errores mejorado
    if not st.session_state.proceso_estado['iniciado']:
            try:
                # Debug: Mostrar información antes de crear el curso
                st.write("Intentando crear curso con:")
                st.write({
                    "nombre": st.session_state.nombre_curso,
                    "código": st.session_state.codigo_curso
                })
                
                # 1. Intentar crear el curso primero
                estado_container.info("Creando curso en Supabase...")
                curso_creado = db.crear_curso(
                    st.session_state.nombre_curso,
                    st.session_state.codigo_curso
                )
                
                if curso_creado:
                    st.session_state.proceso_estado['iniciado'] = True
                    st.session_state.proceso_estado['curso_creado'] = True
                    estado_container.success("✅ Curso creado exitosamente en Supabase")
                    st.rerun()
                else:
                    estado_container.error("❌ Error: No se pudo crear el curso en Supabase")
                    st.write("Por favor, verifica la conexión con la base de datos")
                    return
                    
            except Exception as e:
                estado_container.error(f"❌ Error al crear el curso: {str(e)}")
                st.write("Detalles del error:", {
                    "tipo": type(e).__name__,
                    "mensaje": str(e)
                })
                return

    # Proceso de agregar alumnos si el curso fue creado
    if st.session_state.proceso_estado['iniciado'] and st.session_state.proceso_estado['curso_creado']:
        try:
            estado_container.info("Agregando alumnos a Supabase...")
            progress_bar = st.progress(0)
            
            # Continuar desde donde quedamos
            start_idx = st.session_state.proceso_estado['alumnos_agregados']
            
            for idx, row in df.iloc[start_idx:].iterrows():
                try:
                    # Debug: Mostrar intento de agregar alumno
                    st.write(f"Intentando agregar alumno: {row['Apellido']}, {row['Nombre']}")
                    
                    resultado = db.agregar_alumno(
                        st.session_state.codigo_curso,
                        row['Apellido'].strip(),
                        row['Nombre'].strip()
                    )
                    
                    if resultado:
                        st.session_state.proceso_estado['alumnos_agregados'] += 1
                    else:
                        st.session_state.proceso_estado['errores'].append(
                            f"No se pudo agregar: {row['Apellido']}, {row['Nombre']}"
                        )
                    
                    # Actualizar progreso
                    progress = (st.session_state.proceso_estado['alumnos_agregados'] / len(df))
                    progress_bar.progress(progress)
                    
                except Exception as e:
                    st.session_state.proceso_estado['errores'].append(
                        f"Error al agregar {row['Apellido']}, {row['Nombre']}: {str(e)}"
                    )
            
            # Marcar como completado si llegamos al final
            if st.session_state.proceso_estado['alumnos_agregados'] == len(df):
                st.session_state.proceso_estado['completado'] = True
                estado_container.success("✅ Proceso completado exitosamente!")

        except Exception as e:
            estado_container.error(f"❌ Error en el proceso: {str(e)}")
            st.write("Detalles del error:", {
                "tipo": type(e).__name__,
                "mensaje": str(e)
            })

def descargar_plantillas():
    st.header("Plantillas de Importación")
    
    # Plantilla Excel
    df_ejemplo = pd.DataFrame([
        ['García', 'Juan'],
        ['López', 'María'],
        ['Martínez', 'Carlos']
    ], columns=['Apellido', 'Nombre'])
    
    # Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_ejemplo.to_excel(writer, sheet_name='Alumnos', index=False)
    
    st.download_button(
        label="Descargar Plantilla Excel",
        data=buffer.getvalue(),
        file_name="plantilla_alumnos.xlsx",
        mime="application/vnd.ms-excel"
    )
    
    # CSV
    csv = df_ejemplo.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Descargar Plantilla CSV",
        data=csv,
        file_name="plantilla_alumnos.csv",
        mime="text/csv"
    )
    
    # Mostrar ejemplo
    st.subheader("Ejemplo de formato esperado:")
    st.dataframe(df_ejemplo)
    
    st.info("""
    **Instrucciones:**
    1. Descargue la plantilla en el formato de su preferencia
    2. Complete la información siguiendo el formato mostrado
    3. Asegúrese de:
       - No dejar campos vacíos
       - No tener alumnos duplicados
       - Mantener los nombres de las columnas
    4. Guarde el archivo y súbalo en la pestaña "Importar Datos"
    """)