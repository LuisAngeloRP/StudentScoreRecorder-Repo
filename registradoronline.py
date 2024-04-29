import streamlit as st
import pandas as pd
import os

# Obtener la lista de archivos de la carpeta cursos
archivos_cursos = os.listdir("cursos")

# Función para leer el archivo de alumnos de un curso seleccionado
@st.cache_data
def leer_alumnos_curso(curso):
    ruta_archivo = os.path.join("cursos", curso)
    with open(ruta_archivo, "r") as file:
        estudiantes = []
        for line in file:
            partes = line.strip().split(" ")
            if len(partes) >= 3:
                apellido1 = partes[0]
                apellido2 = partes[1]
                nombre = " ".join(partes[2:])
                apellido = f"{apellido1} {apellido2}"
                estudiantes.append({"apellido": apellido, "nombre": nombre})
    return estudiantes

# Definir la función para registrar puntajes
@st.cache_data
def registrar_puntajes(nombre_sesion, fecha_actual, puntajes, curso):
    estudiantes = leer_alumnos_curso(curso)
    # Crear un DataFrame con los datos de la tabla
    data = []
    for i, estudiante in enumerate(estudiantes):
        data.append(
            {
                "Apellido": estudiante["apellido"],
                "Nombre": estudiante["nombre"],
                nombre_sesion + f" ({fecha_actual})": puntajes[i],
            }
        )

    df_nuevo = pd.DataFrame(data)

    # Crear el nombre del archivo con el nombre del curso
    nombre_archivo = f"Registro_Puntajes_{curso}.xlsx"

    if os.path.exists(nombre_archivo):
        # Si el archivo ya existe, leerlo y agregar una nueva columna para la sesión actual
        df_existente = pd.read_excel(nombre_archivo)
        df_existente[nombre_sesion + f" ({fecha_actual})"] = df_nuevo[nombre_sesion + f" ({fecha_actual})"]
        df_existente.to_excel(nombre_archivo, index=False)
    else:
        # Si el archivo no existe, guardar el DataFrame completo en un nuevo archivo Excel
        df_nuevo.to_excel(nombre_archivo, index=False)

    # Mostrar mensaje de puntajes registrados correctamente
    mensaje = f"Puntajes del curso '{curso}' en la sesión '{nombre_sesion}' correctamente registrados"
    st.success(mensaje)

    return nombre_archivo

# Definir la función para limpiar la lista de puntajes
def limpiar_lista(est_curso):
    return [0] * len(est_curso)

def crear_tabla(estudiantes_curso):
    # Almacenar los puntajes originales
    puntajes_originales = st.session_state.puntajes.copy()
    
    for i, estudiante in enumerate(estudiantes_curso):
        apellido_nombre = f"{estudiante['apellido']} {estudiante['nombre']}"
        puntaje = puntajes_originales[i]  # Obtener el puntaje original
        nuevo_puntaje = st.number_input(
            f"{apellido_nombre}", value=puntaje
        )
        # Actualizar los puntajes en st.session_state solo si han cambiado
        if nuevo_puntaje != puntaje:
            st.session_state.puntajes[i] = nuevo_puntaje
            # Si se ha modificado algo en st.number_input, ejecutar st.rerun()
            st.rerun()

# Función para filtrar la lista de estudiantes según el texto de búsqueda
def filtrar_estudiantes(estudiantes, texto_busqueda):
    return [estudiante for estudiante in estudiantes if texto_busqueda.lower() in f"{estudiante['apellido']} {estudiante['nombre']}".lower()]

# Crear la aplicación Streamlit
def main():
    st.title("Sistema de Participaciones BETA v0.1")

    # Cuadro desplegable para seleccionar el curso en el sidebar
    curso_seleccionado = st.sidebar.selectbox("Selecciona el curso", archivos_cursos)

    # Cuadro de texto para ingresar el nombre de la sesión en el sidebar
    nombre_sesion = st.sidebar.text_input("Ingrese el nombre de la sesión")

    # Cuadro desplegable para seleccionar fecha en el sidebar
    fecha_actual = st.sidebar.date_input("Selecciona la fecha", pd.Timestamp.today())

    # Obtener los estudiantes del curso seleccionado
    estudiantes_curso = leer_alumnos_curso(curso_seleccionado)

    # Widget de búsqueda para filtrar estudiantes por nombre o apellido
    texto_busqueda = st.text_input("Buscar Estudiante")
    st.markdown("---")


    # Filtrar estudiantes según el texto de búsqueda
    if texto_busqueda:
        estudiantes_curso = filtrar_estudiantes(estudiantes_curso, texto_busqueda)

    # Inicializar st.session_state si no está definido
    if "puntajes" not in st.session_state:
        st.session_state.puntajes = limpiar_lista(estudiantes_curso)

    st.sidebar.markdown("---")

    crear_tabla(estudiantes_curso)

    # Botón para limpiar la lista de puntajes en el sidebar
    if st.sidebar.button("Limpiar Lista"):
        st.session_state.puntajes = limpiar_lista(estudiantes_curso)
        st.success("Lista de puntajes limpiada")
    nombre_archivo = registrar_puntajes(nombre_sesion, fecha_actual.strftime("%d_%m_%Y"), st.session_state.puntajes, curso_seleccionado)


    # Botón para registrar puntajes en el sidebar
    if st.sidebar.button("Registrar Puntajes"):
        try:
            with open(nombre_archivo, "rb") as file:
                data = file.read()
                st.download_button(
                    label="Descargar archivo Excel",
                    data=data,
                    file_name=nombre_archivo,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
        except FileNotFoundError:
            st.warning(
                "No se encontró el archivo Excel. Por favor, primero registra los puntajes."
            )

    # Botón para visualizar el archivo Excel en el sidebar
    if st.sidebar.button("Visualizar Excel"):
        try:
            df = pd.read_excel(nombre_archivo)
            st.dataframe(df)
        except FileNotFoundError:
            st.warning("No se encontró el archivo Excel. Por favor, primero registra los puntajes.")


if __name__ == "__main__":
    main()
