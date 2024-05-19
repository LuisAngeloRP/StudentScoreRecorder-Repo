import streamlit as st
import pandas as pd
import os
import base64

def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">{file_label}</a>'
    return href

# Función para crear un curso
def crear_curso(nombre_curso):
    try:
        os.makedirs(os.path.join("cursos", nombre_curso))
        st.success(f"Curso '{nombre_curso}' creado exitosamente!")
    except FileExistsError:
        st.warning(f"¡El curso '{nombre_curso}' ya existe!")

def crear_sesion(curso, nombre_sesion, puntaje_maximo, fecha_sesion):
    try:
        ruta_curso = os.path.join("cursos", curso)
        if not os.path.exists(ruta_curso):
            st.warning(f"No se encontró el curso '{curso}'. Cree el curso antes de agregar sesiones.")
            return
        st.success(f"Sesión '{nombre_sesion}' creada exitosamente en el curso '{curso}'!")
    except Exception as e:
        st.error(f"Error al crear la sesión: {e}")


# Función para obtener la lista de cursos existentes
def obtener_lista_cursos():
    cursos = [nombre for nombre in os.listdir("cursos") if os.path.isdir(os.path.join("cursos", nombre))]
    return cursos

# Función para leer el archivo de alumnos de un curso seleccionado
@st.cache_data
def leer_alumnos_curso(curso):
    ruta_archivo = os.path.join("cursos", curso, "alumnos.txt")
    with open(ruta_archivo, "r") as file:
        estudiantes = []
        for line in file:
            partes = line.strip().split(" ")
            if len(partes) >= 3:
                apellido1 = partes[0]
                apellido2 = partes[1]
                nombre = " ".join(partes[2:])
                apellido = f"{apellido1} {apellido2}"
                estudiantes.append({"Apellido": apellido, "Nombre": nombre, "Puntaje": 0})
    return pd.DataFrame(estudiantes)

# Función para actualizar los puntajes de los alumnos seleccionados
@st.cache
def actualizar_puntaje(curso, df_alumnos):
    try:
        ruta_archivo = os.path.join("cursos", curso, "alumnos.txt")
        df_alumnos.to_csv(ruta_archivo, sep=" ", index=False, header=False)
        st.success("¡Puntos actualizados para los alumnos seleccionados!")
    except Exception as e:
        st.error(f"Error al actualizar los puntajes: {e}")

# Función para validar el puntaje máximo por sesión antes de guardar el archivo CSV
def validar_puntaje_maximo(df_sesion_guardada, puntaje_maximo):
    if df_sesion_guardada["Puntaje"].max() > puntaje_maximo:
        st.warning(f"El puntaje máximo por sesión es {puntaje_maximo}. ¡Corrija los puntajes antes de guardar!")
        return False
    return True

# Crear la aplicación Streamlit
def main():
    st.title("Sistema de Participaciones BETA v0.5")

    # Opciones del sidebar
    option = st.sidebar.selectbox('Selecciona una opción', ['Crear Curso', 'Nueva Sesión', 'Sesiones Guardadas', 'Tabla de Resumen'], index=1)

    if option == 'Crear Curso':
        crear_curso_ui()
    elif option == 'Nueva Sesión':
        nueva_sesion_ui()
    elif option == 'Sesiones Guardadas':
        sesiones_guardadas_tab()
    elif option == 'Tabla de Resumen':
        tabla_resumen()

# UI para crear un nuevo curso
def crear_curso_ui():
    st.subheader("Crear un Nuevo Curso")
    nombre_curso = st.text_input("Nombre del Curso")
    if st.button("Crear Curso"):
        if nombre_curso:
            crear_curso(nombre_curso)
        else:
            st.warning("Ingrese un nombre para el curso.")

def crear_tabla(estudiantes_curso):
    # Almacenar los puntajes originales
    puntajes_originales = st.session_state.puntajes.copy()
    
    for i, estudiante in enumerate(estudiantes_curso):
        apellido_nombre = f"{estudiante['Apellido']} {estudiante['Nombre']}"
        puntaje = puntajes_originales[i]  # Obtener el puntaje original
        nuevo_puntaje = st.number_input(
            f"{apellido_nombre}", value=puntaje
        )
        # Actualizar los puntajes en st.session_state solo si han cambiado
        if nuevo_puntaje != puntaje:
            st.session_state.puntajes[i] = nuevo_puntaje
            # Si se ha modificado algo en st.number_input, ejecutar st.rerun()
            st.rerun()

def nueva_sesion_ui():
    st.sidebar.subheader("Agregar Nueva Sesión")

    cursos = obtener_lista_cursos()
    if not cursos:
        st.sidebar.warning("No hay cursos creados. Cree un curso antes de agregar sesiones.")
        return

    # Selección del curso
    curso_seleccionado = st.sidebar.selectbox("Selecciona el curso", cursos)

    # Nombre de la sesión
    nombre_sesion = st.sidebar.text_input("Nombre de la Sesión", "Sesión 1")

    # Puntaje máximo por sesión
    puntaje_maximo = st.sidebar.number_input("Puntaje Máximo por Sesión", value=20)

    # Fecha de la sesión
    fecha_sesion = st.sidebar.date_input("Fecha de la Sesión", pd.Timestamp.now())

    st.subheader("Información de la Sesión Actual")
    st.write(f"Curso: {curso_seleccionado}")
    st.write(f"Nombre de la Sesión: {nombre_sesion}")
    st.write(f"Puntaje Máximo por Sesión: {puntaje_maximo}")
    st.write(f"Fecha de la Sesión: {fecha_sesion.strftime('%Y-%m-%d')}")

    # Obtener los alumnos del curso seleccionado
    df_alumnos = leer_alumnos_curso(curso_seleccionado)

    # Inicializar st.session_state.puntajes si no está inicializado
    if 'puntajes' not in st.session_state:
        st.session_state.puntajes = df_alumnos['Puntaje'].tolist()

    # Reorganizar el dataframe para colocar la columna "Seleccionado" al principio
    df_alumnos = df_alumnos[['Apellido', 'Nombre', 'Puntaje']]

    edited_df = st.data_editor(df_alumnos, key="editable_df")  # Hacer el dataframe editable

    # Botón para guardar el dataframe
    if st.sidebar.button("Guardar"):
        nombre_archivo = f"{nombre_sesion}_{puntaje_maximo}_{fecha_sesion.strftime('%Y-%m-%d')}.csv"
        ruta_archivo = os.path.join("cursos", curso_seleccionado, nombre_archivo)
        if not os.path.exists(ruta_archivo):
            if validar_puntaje_maximo(edited_df, puntaje_maximo):
                with st.spinner(f"Guardando {nombre_archivo}..."):
                    edited_df.to_csv(ruta_archivo, index=False)
                st.success(f"{nombre_archivo} guardado exitosamente!")

                # Mostrar enlace de descarga
                st.markdown(get_binary_file_downloader_html(ruta_archivo, 'Descargar archivo'), unsafe_allow_html=True)
        else:
            st.sidebar.warning(f"¡El archivo '{nombre_archivo}' ya existe en el curso '{curso_seleccionado}'.")

    # Opción para tomar puntajes con la función `crear_tabla`
    if st.sidebar.checkbox("Tomar puntajes con función crear_tabla"):
        crear_tabla(df_alumnos.to_dict('records'))  # Pasar los datos de los alumnos a la función crear_tabla




def sesiones_guardadas_tab():
    st.subheader("Selecciona una Sesión Guardada")
    cursos = obtener_lista_cursos()
    if not cursos:
        st.warning("No hay cursos creados.")
        return
    
    curso_seleccionado = st.selectbox("Selecciona un Curso", cursos)
    ruta_curso = os.path.join("cursos", curso_seleccionado)
    sesiones_guardadas = [file for file in os.listdir(ruta_curso) if file.endswith('.csv')]

    if sesiones_guardadas:
        sesion_seleccionada = st.selectbox("Sesiones Guardadas", sesiones_guardadas)

        if sesion_seleccionada:
            ruta_sesion = os.path.join(ruta_curso, sesion_seleccionada)
            df_sesion_guardada = pd.read_csv(ruta_sesion)
            edited_df = st.data_editor(df_sesion_guardada, key="editable_df")  # Hacer el dataframe editable

            # Botón para guardar los cambios
            if st.button("Guardar Cambios"):
                puntaje_maximo = int(sesion_seleccionada.split('_')[1])  # Obtener el puntaje máximo de la sesión guardada
                if validar_puntaje_maximo(edited_df, puntaje_maximo):
                    df_sesion_guardada = edited_df
                    df_sesion_guardada.to_csv(ruta_sesion, index=False)
                    st.success("Cambios guardados exitosamente!")
    else:
        st.info("No hay sesiones guardadas en este curso.")

def tabla_resumen():
    st.subheader("Tabla de Resumen de Todos los Cursos")
    cursos = obtener_lista_cursos()

    if cursos:
        for curso in cursos:
            st.subheader(f"Curso: {curso}")
            ruta_curso = os.path.join("cursos", curso)
            sesiones_guardadas = [file for file in os.listdir(ruta_curso) if file.endswith('.csv')]

            if sesiones_guardadas:
                # Crear un diccionario para almacenar los datos de las sesiones guardadas
                datos_sesiones = {}

                # Leer los datos de las sesiones guardadas y almacenarlos en el diccionario
                for sesion in sesiones_guardadas:
                    nombre_sesion = sesion.split('_')[0]
                    fecha_sesion = sesion.split('_')[2].split('.')[0]
                    df_sesion = pd.read_csv(os.path.join(ruta_curso, sesion))
                    datos_sesiones[f"{nombre_sesion} ({fecha_sesion})"] = df_sesion['Puntaje']

                # Crear un DataFrame con los datos del diccionario
                df_resumen = pd.DataFrame(datos_sesiones)

                # Obtener los apellidos y nombres de los alumnos del primer curso
                df_alumnos = leer_alumnos_curso(curso)
                
                # Agregar las columnas de apellidos y nombres al principio del DataFrame de resumen
                df_resumen = pd.concat([df_alumnos[['Apellido', 'Nombre']], df_resumen], axis=1)

                # Mostrar la tabla de resumen
                st.dataframe(df_resumen)
            else:
                st.info(f"No hay sesiones guardadas en el curso '{curso}'.")
    else:
        st.warning("No hay cursos creados.")


if __name__ == "__main__":
    main()
