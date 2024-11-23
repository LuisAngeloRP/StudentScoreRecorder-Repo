import streamlit as st
import pandas as pd
from datetime import datetime
import time

from supabase import create_client

class ImportManager:
    def __init__(self, db_client):
        self.db = db_client
        self.initialize_session_state()

    def initialize_session_state(self):
        """Inicializa o recupera el estado de la sesión"""
        if 'import_state' not in st.session_state:
            st.session_state.import_state = {
                'curso_info': None,
                'alumnos_data': None,
                'proceso_completado': False,
                'errores': []
            }

    def reset_state(self):
        """Reinicia el estado de importación"""
        st.session_state.import_state = {
            'curso_info': None,
            'alumnos_data': None,
            'proceso_completado': False,
            'errores': []
        }

    def render_curso_form(self):
        """Renderiza el formulario de información del curso"""
        st.subheader("1. Información del Curso")
        
        with st.form("curso_form"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre del Curso", 
                                     placeholder="Ej: Matemáticas 2024-1")
            with col2:
                codigo = st.text_input("Código del Curso", 
                                     placeholder="Ej: MAT101")
            
            submit = st.form_submit_button("Validar Curso")
            
            if submit:
                if not nombre or not codigo:
                    st.error("Complete todos los campos del curso")
                    return False
                
                # Verificar si el código ya existe
                try:
                    cursos_existentes = self.db.table('cursos').select('codigo').eq('codigo', codigo).execute()
                    if cursos_existentes.data:
                        st.error("Este código de curso ya existe")
                        return False
                    
                    st.session_state.import_state['curso_info'] = {
                        'nombre': nombre,
                        'codigo': codigo
                    }
                    st.success("Información del curso validada")
                    return True
                    
                except Exception as e:
                    st.error(f"Error al verificar el curso: {str(e)}")
                    return False
        
        return False

    def render_alumnos_import(self):
        """Renderiza la sección de importación de alumnos"""
        st.subheader("2. Lista de Alumnos")
        
        tipo_importacion = st.radio(
            "Método de importación:",
            ["Archivo Excel/CSV", "Copiar y pegar", "Manual"],
            horizontal=True
        )
        
        if tipo_importacion == "Archivo Excel/CSV":
            self.import_from_file()
        elif tipo_importacion == "Copiar y pegar":
            self.import_from_text()
        else:
            self.import_manual()

    def import_from_file(self):
        """Maneja la importación desde archivo"""
        file = st.file_uploader("Subir archivo", type=['xlsx', 'csv'])
        if file:
            try:
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)
                
                if self.validate_dataframe(df):
                    st.session_state.import_state['alumnos_data'] = df
                    self.show_preview()
            except Exception as e:
                st.error(f"Error al leer el archivo: {str(e)}")

    def import_from_text(self):
        """Maneja la importación desde texto"""
        st.info("Formato esperado: Apellido,Nombre")
        texto = st.text_area(
            "Pegue los datos aquí",
            height=200,
            placeholder="García,Juan\nLópez,María"
        )
        
        if st.button("Procesar"):
            try:
                lines = [line.strip().split(',') for line in texto.strip().split('\n')]
                df = pd.DataFrame(lines, columns=['Apellido', 'Nombre'])
                if self.validate_dataframe(df):
                    st.session_state.import_state['alumnos_data'] = df
                    self.show_preview()
            except Exception as e:
                st.error(f"Error al procesar el texto: {str(e)}")

    def import_manual(self):
        """Maneja la importación manual"""
        if 'temp_alumnos' not in st.session_state:
            st.session_state.temp_alumnos = []
        
        with st.form("alumno_form"):
            col1, col2 = st.columns(2)
            with col1:
                apellido = st.text_input("Apellido")
            with col2:
                nombre = st.text_input("Nombre")
            
            if st.form_submit_button("Agregar Alumno"):
                if apellido and nombre:
                    st.session_state.temp_alumnos.append([apellido, nombre])
                    st.success("Alumno agregado")
        
        if st.session_state.temp_alumnos:
            df = pd.DataFrame(st.session_state.temp_alumnos, columns=['Apellido', 'Nombre'])
            st.session_state.import_state['alumnos_data'] = df
            self.show_preview()

    def validate_dataframe(self, df):
        """Valida el formato del DataFrame"""
        if not all(col in df.columns for col in ['Apellido', 'Nombre']):
            st.error("El archivo debe contener las columnas: Apellido, Nombre")
            return False
        
        if df.empty:
            st.error("No hay datos para importar")
            return False
        
        if df['Apellido'].isna().any() or df['Nombre'].isna().any():
            st.error("Existen datos vacíos")
            return False
        
        duplicados = df.duplicated(subset=['Apellido', 'Nombre'], keep=False)
        if duplicados.any():
            st.error("Existen alumnos duplicados")
            st.dataframe(df[duplicados])
            return False
        
        return True

    def show_preview(self):
        """Muestra la vista previa de los datos y el botón de importación"""
        st.write("### Vista previa")
        st.dataframe(st.session_state.import_state['alumnos_data'])
        
        if st.button("Importar Datos"):
            self.process_import()

    def process_import(self):
        """Procesa la importación de datos"""
        try:
            with st.spinner("Procesando importación..."):
                # 1. Crear curso
                curso_data = st.session_state.import_state['curso_info']
                response = self.db.table('cursos').insert({
                    'nombre': curso_data['nombre'],
                    'codigo': curso_data['codigo'],
                    'created_at': datetime.now().isoformat()
                }).execute()
                
                if not response.data:
                    raise Exception("Error al crear el curso")
                
                curso_id = response.data[0]['id']
                
                # 2. Agregar alumnos
                alumnos_data = st.session_state.import_state['alumnos_data']
                total = len(alumnos_data)
                progress_bar = st.progress(0)
                
                for idx, row in alumnos_data.iterrows():
                    self.db.table('alumnos').insert({
                        'curso_id': curso_id,
                        'apellido': row['Apellido'].strip(),
                        'nombre': row['Nombre'].strip(),
                        'created_at': datetime.now().isoformat()
                    }).execute()
                    
                    progress_bar.progress((idx + 1) / total)
                
                st.success(f"""
                ✅ Importación completada exitosamente!
                - Curso: {curso_data['nombre']}
                - Alumnos importados: {total}
                """)
                
                # Reiniciar estado
                if st.button("Nueva Importación"):
                    self.reset_state()
                    st.experimental_rerun()
                
        except Exception as e:
            st.error(f"Error durante la importación: {str(e)}")
            st.session_state.import_state['errores'].append(str(e))

def main():
    st.title("Importación de Cursos y Alumnos")
    
    # Inicializar cliente de base de datos (Supabase)
    supabase = create_client(st.secrets["supabase_url"], st.secrets["supabase_key"])
    
    # Crear instancia del gestor de importación
    import_manager = ImportManager(supabase)
    
    # Renderizar interfaz
    if not st.session_state.import_state['curso_info']:
        import_manager.render_curso_form()
    elif not st.session_state.import_state['proceso_completado']:
        import_manager.render_alumnos_import()

if __name__ == "__main__":
    main()