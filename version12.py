import streamlit as st
import pandas as pd
import os

# Obtener la lista de archivos de la carpeta cursos
archivos_cursos = os.listdir("cursos")

# Función para leer el archivo de alumnos de un curso seleccionado

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
def limpiar_lista(curso_estudiantes):
    st.session_state.puntajes = [0] * len(curso_estudiantes)
    st.success("Lista de puntajes limpiada")

# Crear la aplicación Streamlit
def main():
    st.title("Puntos Ciencia de datos y seguridad de la información")

    # Cuadro desplegable para seleccionar el curso
    curso_seleccionado = st.selectbox("Selecciona el curso", archivos_cursos)

    # Cuadro de texto para ingresar el nombre de la sesión
    nombre_sesion = st.text_input("Ingrese el nombre de la sesión")

    # Cuadro desplegable para seleccionar fecha
    fecha_actual = st.date_input("Selecciona la fecha", pd.Timestamp.today())

    # Obtener los estudiantes del curso seleccionado
    estudiantes_curso = leer_alumnos_curso(curso_seleccionado)

    # Inicializar st.session_state si no está definido
    if "puntajes" not in st.session_state:
        st.session_state.puntajes = [0] * len(estudiantes_curso)

    # Crear la tabla de asistencia
    st.write("### Tabla de Puntajes")
    for i, estudiante in enumerate(estudiantes_curso):
        apellido_nombre = f"{estudiante['apellido']} {estudiante['nombre']}"
        st.session_state.puntajes[i] = st.number_input(
            f"{apellido_nombre}", value=st.session_state.puntajes[i]
        )

    # Botón para limpiar la lista de puntajes
    if st.button("Limpiar Lista"):
        limpiar_lista(estudiantes_curso)

    # Botón para registrar puntajes
    if st.button("Registrar Puntajes"):
        nombre_archivo = registrar_puntajes(nombre_sesion, fecha_actual.strftime("%d_%m_%Y"), st.session_state.puntajes, curso_seleccionado)
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

    # Botón para visualizar el archivo Excel
    if st.button("Visualizar Excel"):
        try:
            df = pd.read_excel(nombre_archivo)
            st.dataframe(df)
        except FileNotFoundError:
            st.warning("No se encontró el archivo Excel. Por favor, primero registra los puntajes.")

if __name__ == "__main__":
    main()
