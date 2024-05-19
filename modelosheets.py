import streamlit as st
import pandas as pd
import os
import base64
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import time

def tabla_resumen_curso():
    st.subheader("Tabla de Resumen")

    # Obtener la lista de cursos disponibles
    indices_cursos, nombres_cursos = obtener_lista_cursos()
    
    if not indices_cursos:
        st.warning("No hay cursos creados.")
        return
    
    curso_seleccionado = st.sidebar.selectbox("Selecciona el curso", nombres_cursos)
    indice_curso_seleccionado = indices_cursos[nombres_cursos.index(curso_seleccionado)]

    # Verificar si se ha seleccionado un curso
    if curso_seleccionado:
        # Mostrar la tabla resumen para el curso seleccionado
        tabla_resumen_curso_individual(indice_curso_seleccionado)

def tabla_resumen_curso_individual(nombre_curso):
    st.subheader(f"Tabla Resumen del Curso: {nombre_curso}")
    
    # Obtener todas las sesiones guardadas para el curso
    conn = st.connection(nombre_curso, type=GSheetsConnection)
    df_sesiones = conn.read(worksheet="sesiones", ttl=0)
    
    if df_sesiones is None or df_sesiones.empty:
        st.warning("No hay sesiones guardadas en este curso.")
        return
    
    # Eliminar valores NaN
    df_sesiones = df_sesiones.dropna(subset=['sesiones']).reset_index(drop=True)
    sesiones_guardadas = df_sesiones['sesiones'].tolist()
    
    if not sesiones_guardadas:
        st.warning("No hay sesiones guardadas en este curso.")
        return
    
    # Crear la tabla resumen
    tabla_resumen = pd.DataFrame(columns=["Alumno"] + sesiones_guardadas)
    
    # Obtener la lista de estudiantes de la primera sesión
    df_primera_sesion = conn.read(worksheet=sesiones_guardadas[0], ttl=0)
    estudiantes = [" ".join([apellido, nombre]) for apellido, nombre in zip(df_primera_sesion["Apellido"], df_primera_sesion["Nombre"])]

    # Agregar la lista de estudiantes a la tabla resumen
    tabla_resumen["Alumno"] = estudiantes
    
    # Agregar los puntajes de cada sesión
    for sesion in sesiones_guardadas:
        df_sesion_guardada = conn.read(worksheet=sesion, ttl=0)
        tabla_resumen[sesion] = df_sesion_guardada['Puntaje']
    
    # Mostrar la tabla resumen
    st.dataframe(tabla_resumen)



#Listos

# Función para validar el puntaje máximo por sesión antes de guardar el archivo CSV
def validar_puntaje_maximo(df_sesion_guardada, puntaje_maximo):
    if df_sesion_guardada["Puntaje"].max() > puntaje_maximo:
        st.sidebar.warning(f"El puntaje máximo por sesión es {puntaje_maximo}. ¡Corrija los puntajes antes de guardar!")
        return False
    return True

def sesiones_guardadas_tab():
    st.subheader("Selecciona una Sesión Guardada")
    indices_cursos, nombres_cursos = obtener_lista_cursos()
    
    if not indices_cursos:
        st.warning("No hay cursos creados.")
        return
    
    curso_seleccionado = st.sidebar.selectbox("Selecciona un Curso", nombres_cursos)
    indice_curso_seleccionado = indices_cursos[nombres_cursos.index(curso_seleccionado)]

    conn = st.connection(indice_curso_seleccionado, type=GSheetsConnection)

    # Obtener la lista de sesiones guardadas desde el DataFrame de Google Sheets
    df_sesiones = conn.read(worksheet="sesiones", ttl=0)

    if df_sesiones is None or df_sesiones.empty:
        st.info("No hay sesiones guardadas en este curso.")
        return

    # Eliminar valores NaN
    df_sesiones = df_sesiones.dropna(subset=['sesiones']).reset_index(drop=True)
    sesiones_guardadas = df_sesiones['sesiones'].tolist()

    if not sesiones_guardadas:
        st.info("No hay sesiones guardadas en este curso.")
        return

    sesion_seleccionada = st.sidebar.selectbox("Sesiones Guardadas", sesiones_guardadas)

    if sesion_seleccionada:
        # Leer los datos de la sesión guardada desde Google Sheets
        df_sesion_guardada = conn.read(worksheet=sesion_seleccionada, ttl=0)
        df_sesion_guardada = df_sesion_guardada.dropna(how='all').reset_index(drop=True)  # Eliminar filas completamente NaN

        crear_tabla(df_sesion_guardada)  # Crear la tabla de puntajes

        # Verificar si ha habido cambios y guardar automáticamente
        if 'sesion_guardada' not in st.session_state or st.session_state.sesion_guardada != df_sesion_guardada.to_json():
            st.session_state.sesion_guardada = df_sesion_guardada.to_json()
            puntaje_maximo = int(sesion_seleccionada.split('_')[1])  # Obtener el puntaje máximo de la sesión guardada
            if validar_puntaje_maximo(df_sesion_guardada, puntaje_maximo):
                # Guardar los cambios en Google Sheets
                conn.update(worksheet=sesion_seleccionada, data=df_sesion_guardada)
                st.success("Cambios guardados exitosamente!")

def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">{file_label}</a>'
    return href

# Crear la aplicación Streamlit
def main():
    st.title("Sistema de Participaciones v1")

    # Opciones del sidebar
    option = st.sidebar.selectbox('Selecciona una opción', ['Nueva Sesión', 'Sesiones Guardadas', 'Tabla de Resumen'], index=0)

    
    if option == 'Nueva Sesión':
        nueva_sesion_ui()
    elif option == 'Sesiones Guardadas':
        sesiones_guardadas_tab()
    elif option == 'Tabla de Resumen':
        tabla_resumen_curso()
    #elif option == 'Crear Curso':
    #    crear_curso_ui()

def crear_tabla(df_alumnos):
    # Almacenar los puntajes originales
    puntajes_originales = df_alumnos['Puntaje'].tolist()

    for i, estudiante in enumerate(df_alumnos.itertuples(), start=1):
        apellido_nombre = f"{i}. {estudiante.Apellido} {estudiante.Nombre}"
        puntaje = puntajes_originales[i - 1]  # Obtener el puntaje original
        nuevo_puntaje = st.number_input(
            f"{apellido_nombre}", value=puntaje, key=f"puntaje_{i}"
        )
        # Actualizar los puntajes en el DataFrame solo si han cambiado
        if nuevo_puntaje != puntaje:
            df_alumnos.at[estudiante.Index, 'Puntaje'] = nuevo_puntaje

def nueva_sesion_ui():
    st.sidebar.subheader("Agregar Nueva Sesión")

    indices_cursos, nombres_cursos = obtener_lista_cursos()
    if not indices_cursos:
        st.sidebar.warning("No hay cursos creados. Cree un curso antes de agregar sesiones.")
        return

    # Selección del curso
    curso_seleccionado = st.sidebar.selectbox("Selecciona el curso", nombres_cursos)
    indice_curso_seleccionado = indices_cursos[nombres_cursos.index(curso_seleccionado)]

    # Nombre de la sesión
    nombre_sesion = st.sidebar.text_input("Nombre de la Sesión", "Sesión 1")

    # Puntaje máximo por sesión
    puntaje_maximo = st.sidebar.number_input("Puntaje Máximo por Sesión", value=20)

    # Fecha de la sesión
    fecha_sesion = st.sidebar.date_input("Fecha de la Sesión", pd.Timestamp.now())

    # Obtener los alumnos del curso seleccionado
    df_alumnos = leer_alumnos_curso(indice_curso_seleccionado)

    # Inicializar st.session_state.puntajes si no está inicializado
    if 'puntajes' not in st.session_state:
        st.session_state.puntajes = df_alumnos['Puntaje'].tolist()

    df_alumnos = df_alumnos[['Apellido', 'Nombre', 'Puntaje']]

    edited_df = st.data_editor(df_alumnos, key="editable_df")  # Hacer el dataframe editable

    conn = st.connection(indice_curso_seleccionado, type=GSheetsConnection)
    # Botón para guardar el dataframe
    if st.sidebar.button("Guardar"):
        # Generar el nombre del archivo y de la hoja con el mismo formato
        nombre_archivo_y_hoja = f"{nombre_sesion}_{puntaje_maximo}_{fecha_sesion.strftime('%Y-%m-%d')}.csv"
        ruta_directorio = os.path.join("cursos", curso_seleccionado)
        ruta_archivo = os.path.join(ruta_directorio, nombre_archivo_y_hoja)

        # Crear el directorio si no existe
        if not os.path.exists(ruta_directorio):
            os.makedirs(ruta_directorio)

        if not os.path.exists(ruta_archivo):
            if validar_puntaje_maximo(edited_df, puntaje_maximo):
                with st.spinner(f"Guardando {nombre_archivo_y_hoja}..."):
                    edited_df.to_csv(ruta_archivo, index=False)
                st.success(f"{nombre_archivo_y_hoja} guardado exitosamente!")

                # Añadir el nombre de la sesión al archivo sesiones.csv
                ruta_sesiones = os.path.join("cursos", curso_seleccionado, "sesiones.csv")
                if os.path.exists(ruta_sesiones):
                    sesiones_df = pd.read_csv(ruta_sesiones)
                else:
                    sesiones_df = pd.DataFrame(columns=["sesiones"])

                # Guardar el nombre de la hoja en sesiones.csv sin la extensión .csv
                nombre_sesion_sin_extension = nombre_archivo_y_hoja[:-4]
                sesiones_df = sesiones_df.append({"sesiones": nombre_sesion_sin_extension}, ignore_index=True)
                sesiones_df.to_csv(ruta_sesiones, index=False)

                # Crear una nueva hoja en Google Sheets
                datos_sesion = pd.read_csv(ruta_archivo)  # Leer el archivo CSV
                conn.create(worksheet=nombre_sesion_sin_extension, data=datos_sesion)

                # Leer sesiones de Google Sheets
                df_sesiones = conn.read(worksheet="sesiones", ttl=0)
                print("Contenido leído de Google Sheets (antes de agregar nuevas sesiones):")
                print(df_sesiones)

                # Verificar si df_sesiones no está vacío
                if df_sesiones is None or df_sesiones.empty:
                    df_sesiones_modificado = sesiones_df
                else:
                    # Agregar registros de sesiones.csv al df_sesiones
                    df_sesiones_modificado = pd.concat([df_sesiones, sesiones_df]).drop_duplicates().reset_index(drop=True)

                print("Contenido a subir a Google Sheets (df_sesiones_modificado):")
                print(df_sesiones_modificado)

                # Subir el df_sesiones modificado a Google Sheets
                conn.update(worksheet="sesiones", data=df_sesiones_modificado)

                # Pausa para asegurar que la actualización se complete
                time.sleep(2)

                # Leer sesiones de Google Sheets nuevamente
                df_sesiones_actualizado = conn.read(worksheet="sesiones", ttl=0)
                print("Contenido de Google Sheets después de la actualización:")
                print(df_sesiones_actualizado)

                # Mostrar enlace de descarga
                st.markdown(get_binary_file_downloader_html(ruta_archivo, 'Descargar archivo'), unsafe_allow_html=True)

def obtener_lista_cursos():
    with open("cursos.txt", "r") as file:
        nombres_cursos = file.readlines()
    nombres_cursos = [nombre.strip() for nombre in nombres_cursos]
    cursos = [f"curso{i+1}" for i in range(len(nombres_cursos))]
    return cursos, nombres_cursos

def leer_alumnos_curso(curso):
    conn = st.connection(curso, type=GSheetsConnection)
    df = conn.read(worksheet="alumnos", ttl=0)
    
    estudiantes = []
    for nombre_completo in df["alumnos"]:
        # Convertir el valor a cadena de texto solo si no es un número
        if not isinstance(nombre_completo, (int, float)):
            partes = str(nombre_completo).split(" ")
            if len(partes) >= 2:
                apellido = " ".join(partes[:-1])
                nombre = partes[-1]
                estudiantes.append({"Apellido": apellido, "Nombre": nombre, "Puntaje": 0})
    
    return pd.DataFrame(estudiantes)

if __name__ == "__main__":
    main()
