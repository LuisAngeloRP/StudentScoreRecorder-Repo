import streamlit as st
import pandas as pd
import os
import base64
from streamlit_gsheets import GSheetsConnection

# Función para obtener la lista de cursos
def obtener_lista_cursos():
    with open("cursos.txt", "r") as file:
        nombres_cursos = file.readlines()
    nombres_cursos = [nombre.strip() for nombre in nombres_cursos]
    cursos = [f"curso{i+1}" for i in range(len(nombres_cursos))]
    return cursos, nombres_cursos

# Función para leer los alumnos de un curso
def leer_alumnos_curso(curso):
    conn = st.connection(curso, type=GSheetsConnection)
    df = conn.read(worksheet="alumnos", ttl=0)
    estudiantes = []
    for nombre_completo in df["alumnos"]:
        if not isinstance(nombre_completo, (int, float)):
            partes = str(nombre_completo).split(" ")
            if len(partes) >= 2:
                apellido = " ".join(partes[:-1])
                nombre = partes[-1]
                estudiantes.append({"Apellido": apellido, "Nombre": nombre, "Puntaje": 0})
    return pd.DataFrame(estudiantes)

# Función para validar el puntaje máximo por sesión
def validar_puntaje_maximo(df_sesion_guardada, puntaje_maximo):
    if df_sesion_guardada["Puntaje"].max() > puntaje_maximo:
        st.sidebar.warning(f"El puntaje máximo por sesión es {puntaje_maximo}. ¡Corrija los puntajes antes de guardar!")
        return False
    return True

# Función para crear una tabla editable
def crear_tabla(df_alumnos):
    puntajes_originales = df_alumnos['Puntaje'].tolist()
    for i, estudiante in enumerate(df_alumnos.itertuples(), start=1):
        apellido_nombre = f"{i}. {estudiante.Apellido} {estudiante.Nombre}"
        puntaje = puntajes_originales[i - 1]
        nuevo_puntaje = st.number_input(f"{apellido_nombre}", value=puntaje, key=f"puntaje_{i}")
        if nuevo_puntaje != puntaje:
            df_alumnos.at[estudiante.Index, 'Puntaje'] = nuevo_puntaje

# Función para descargar archivos binarios
# Función para descargar archivos binarios
def get_binary_file_downloader_html(bin_file, file_label='File'):
    # Crear el archivo si no existe
    if not os.path.exists(bin_file):
        with open(bin_file, 'w') as f:
            f.write('')  # Crear archivo vacío

    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">{file_label}</a>'
    return href

# Función para mostrar la tabla de resumen del curso
def tabla_resumen_curso():
    st.subheader("Tabla de Resumen")
    indices_cursos, nombres_cursos = obtener_lista_cursos()
    if not indices_cursos:
        st.warning("No hay cursos creados.")
        return
    curso_seleccionado = st.sidebar.selectbox("Selecciona el curso", nombres_cursos)
    indice_curso_seleccionado = indices_cursos[nombres_cursos.index(curso_seleccionado)]
    if curso_seleccionado:
        tabla_resumen_curso_individual(indice_curso_seleccionado)

# Función para mostrar la tabla de resumen de un curso individual
def tabla_resumen_curso_individual(nombre_curso):
    st.subheader(f"Tabla Resumen del Curso: {nombre_curso}")
    conn = st.connection(nombre_curso, type=GSheetsConnection)
    df_sesiones = conn.read(worksheet="sesiones", ttl=0)
    if df_sesiones is None or df_sesiones.empty:
        st.warning("No hay sesiones guardadas en este curso.")
        return
    df_sesiones = df_sesiones.dropna(subset=['sesiones']).reset_index(drop=True)
    sesiones_guardadas = df_sesiones['sesiones'].tolist()
    if not sesiones_guardadas:
        st.warning("No hay sesiones guardadas en este curso.")
        return
    tabla_resumen = pd.DataFrame(columns=["Alumno"] + sesiones_guardadas)
    df_primera_sesion = conn.read(worksheet=sesiones_guardadas[0], ttl=0)
    estudiantes = [" ".join([apellido, nombre]) for apellido, nombre in zip(df_primera_sesion["Apellido"], df_primera_sesion["Nombre"])]
    tabla_resumen["Alumno"] = estudiantes
    for sesion in sesiones_guardadas:
        df_sesion_guardada = conn.read(worksheet=sesion, ttl=0)
        tabla_resumen[sesion] = df_sesion_guardada['Puntaje']
    st.dataframe(tabla_resumen)

# Función para mostrar las sesiones guardadas
def sesiones_guardadas_tab():
    st.subheader("Selecciona una Sesión Guardada")
    indices_cursos, nombres_cursos = obtener_lista_cursos()
    if not indices_cursos:
        st.warning("No hay cursos creados.")
        return
    curso_seleccionado = st.sidebar.selectbox("Selecciona un Curso", nombres_cursos)
    indice_curso_seleccionado = indices_cursos[nombres_cursos.index(curso_seleccionado)]
    conn = st.connection(indice_curso_seleccionado, type=GSheetsConnection)
    df_sesiones = conn.read(worksheet="sesiones", ttl=0)
    if df_sesiones is None or df_sesiones.empty:
        st.info("No hay sesiones guardadas en este curso.")
        return
    df_sesiones = df_sesiones.dropna(subset=['sesiones']).reset_index(drop=True)
    sesiones_guardadas = df_sesiones['sesiones'].tolist()
    if not sesiones_guardadas:
        st.info("No hay sesiones guardadas en este curso.")
        return
    sesion_seleccionada = st.sidebar.selectbox("Sesiones Guardadas", sesiones_guardadas)
    if sesion_seleccionada:
        df_sesion_guardada = conn.read(worksheet=sesion_seleccionada, ttl=0)
        df_sesion_guardada = df_sesion_guardada.dropna(how='all').reset_index(drop=True)
        crear_tabla(df_sesion_guardada)
        if 'sesion_guardada' not in st.session_state or st.session_state.sesion_guardada != df_sesion_guardada.to_json():
            st.session_state.sesion_guardada = df_sesion_guardada.to_json()
            puntaje_maximo = int(sesion_seleccionada.split('_')[1])
            if validar_puntaje_maximo(df_sesion_guardada, puntaje_maximo):
                conn.update(worksheet=sesion_seleccionada, data=df_sesion_guardada)
                st.success("Cambios guardados exitosamente!")

# Función para agregar una nueva sesión
def nueva_sesion_ui():
    st.sidebar.subheader("Agregar Nueva Sesión")
    indices_cursos, nombres_cursos = obtener_lista_cursos()
    if not indices_cursos:
        st.sidebar.warning("No hay cursos creados. Cree un curso antes de agregar sesiones.")
        return
    curso_seleccionado = st.sidebar.selectbox("Selecciona el curso", nombres_cursos)
    indice_curso_seleccionado = indices_cursos[nombres_cursos.index(curso_seleccionado)]
    nombre_sesion = st.sidebar.text_input("Nombre de la Sesión", "Sesión 1")
    puntaje_maximo = st.sidebar.number_input("Puntaje Máximo por Sesión", value=20)
    fecha_sesion = st.sidebar.date_input("Fecha de la Sesión", pd.Timestamp.now())
    df_alumnos = leer_alumnos_curso(indice_curso_seleccionado)
    if 'puntajes' not in st.session_state:
        st.session_state.puntajes = df_alumnos['Puntaje'].tolist()
    df_alumnos = df_alumnos[['Apellido', 'Nombre', 'Puntaje']]
    edited_df = st.data_editor(df_alumnos, key="editable_df")
    conn = st.connection(indice_curso_seleccionado, type=GSheetsConnection)
    if st.sidebar.button("Guardar"):
        nombre_archivo_y_hoja = f"{nombre_sesion}_{puntaje_maximo}_{fecha_sesion.strftime('%Y-%m-%d')}.csv"
        if validar_puntaje_maximo(edited_df, puntaje_maximo):
            conn.create(worksheet=nombre_archivo_y_hoja[:-4], data=edited_df)
            df_sesiones = conn.read(worksheet="sesiones", ttl=0)
            if df_sesiones is None or df_sesiones.empty:
                df_sesiones = pd.DataFrame(columns=["sesiones"])
            sesiones_df = pd.DataFrame({"sesiones": [nombre_archivo_y_hoja[:-4]]})
            df_sesiones = pd.concat([df_sesiones, sesiones_df]).drop_duplicates().reset_index(drop=True)
            conn.update(worksheet="sesiones", data=df_sesiones)
            st.success(f"{nombre_archivo_y_hoja} guardado exitosamente!")
            st.markdown(get_binary_file_downloader_html(nombre_archivo_y_hoja, 'Descargar archivo'), unsafe_allow_html=True)

# Función para crear una evaluación
def crear_evaluacion_ui():
    st.sidebar.subheader("Crear Evaluación")
    indices_cursos, nombres_cursos = obtener_lista_cursos()
    if not indices_cursos:
        st.sidebar.warning("No hay cursos creados. Cree un curso antes de crear evaluaciones.")
        return
    curso_seleccionado = st.sidebar.selectbox("Selecciona el curso", nombres_cursos)
    indice_curso_seleccionado = indices_cursos[nombres_cursos.index(curso_seleccionado)]
    nombre_evaluacion = st.sidebar.text_input("Nombre de la Evaluación", "Evaluación 1")
    escala = st.sidebar.number_input("Escala de Calificación", value=20)


    conn = st.connection(indice_curso_seleccionado, type=GSheetsConnection)
    df_sesiones = conn.read(worksheet="sesiones", ttl=0)
    if df_sesiones is None or df_sesiones.empty:
        st.sidebar.warning("No hay sesiones guardadas en este curso.")
        return
    df_sesiones = df_sesiones.dropna(subset=['sesiones']).reset_index(drop=True)
    sesiones_guardadas = df_sesiones['sesiones'].tolist()
    sesiones_seleccionadas = st.sidebar.multiselect("Selecciona las sesiones para la evaluación", sesiones_guardadas)

    if st.sidebar.button("Crear Evaluación"):
        if not sesiones_seleccionadas:
            st.sidebar.warning("Debe seleccionar al menos una sesión.")
            return

        # Crear la tabla de evaluación
        df_primera_sesion = conn.read(worksheet=sesiones_seleccionadas[0], ttl=0)
        estudiantes = [" ".join([apellido, nombre]) for apellido, nombre in zip(df_primera_sesion["Apellido"], df_primera_sesion["Nombre"])]
        tabla_evaluacion = pd.DataFrame(columns=["Alumno", "Puntaje Obtenido", "Puntaje Máximo"])
        tabla_evaluacion["Alumno"] = estudiantes

        puntaje_obtenido_total = []
        puntaje_maximo_total = 0

        for sesion in sesiones_seleccionadas:
            df_sesion_guardada = conn.read(worksheet=sesion, ttl=0)
            puntaje_maximo_sesion = int(sesion.split('_')[1])
            puntaje_maximo_total += puntaje_maximo_sesion

            if not puntaje_obtenido_total:
                puntaje_obtenido_total = df_sesion_guardada['Puntaje'].tolist()
            else:
                puntaje_obtenido_total = [x + y for x, y in zip(puntaje_obtenido_total, df_sesion_guardada['Puntaje'].tolist())]

        tabla_evaluacion["Puntaje Obtenido"] = puntaje_obtenido_total
        tabla_evaluacion["Puntaje Máximo"] = puntaje_maximo_total 

        tabla_evaluacion["Resultado"] = tabla_evaluacion["Puntaje Obtenido"] / tabla_evaluacion["Puntaje Máximo"] 

        st.dataframe(tabla_evaluacion)

        # Guardar la evaluación
        nombre_archivo_y_hoja = f"{nombre_evaluacion}_{puntaje_maximo_total}.csv"
        conn.create(worksheet=nombre_archivo_y_hoja[:-4], data=tabla_evaluacion)
        st.success(f"Evaluación {nombre_archivo_y_hoja} creada y guardada exitosamente!")
        st.markdown(get_binary_file_downloader_html(nombre_archivo_y_hoja, 'Descargar evaluación'), unsafe_allow_html=True)

# Función principal para crear la aplicación Streamlit
def main():
    st.title("Sistema de Participaciones v1")
    option = st.sidebar.selectbox('Selecciona una opción', ['Nueva Sesión', 'Sesiones Guardadas', 'Tabla de Resumen', 'Crear Evaluación'], index=0)

    if option == 'Nueva Sesión':
        nueva_sesion_ui()
    elif option == 'Sesiones Guardadas':
        sesiones_guardadas_tab()
    elif option == 'Tabla de Resumen':
        tabla_resumen_curso()
    elif option == 'Crear Evaluación':
        crear_evaluacion_ui()

if __name__ == "__main__":
    main()
