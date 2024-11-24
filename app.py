# home.py
import streamlit as st
from src.config.supabase_manager import SupabaseManager
from src.ui.sesiones import sesiones_ui
from src.ui.sesion_actual import sesion_actual_ui  # Nueva importación
from src.ui.evaluaciones import evaluaciones_ui
from src.ui.importacion import importacion_ui

st.set_page_config(
    page_title="Sistema de Participaciones v2",
    page_icon="📚",
    layout="wide"
)

def main():
    st.title("Sistema de Participaciones v2")
    
    # Inicializar conexión con Supabase
    if 'db' not in st.session_state:
        st.session_state.db = SupabaseManager()
    
    # Menú principal actualizado
    menu_options = {
        "Importar Curso": importacion_ui,
        "Sesiones": sesiones_ui,
        "Sesión Actual": sesion_actual_ui,  # Nueva opción
        "Evaluaciones": evaluaciones_ui
    }
    
    opcion = st.sidebar.radio("Selecciona una opción", list(menu_options.keys()))
    menu_options[opcion](st.session_state.db)

if __name__ == "__main__":
    main()