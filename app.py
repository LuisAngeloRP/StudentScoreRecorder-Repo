import streamlit as st
from src.config.supabase_manager import SupabaseManager
from src.ui.nueva_sesion import nueva_sesion_ui
from src.ui.sesiones_guardadas import sesiones_guardadas_tab
from src.ui.tabla_resumen import tabla_resumen_ui
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
    
    # Menú principal
    menu_options = {
        "Importar Curso": importacion_ui,
        "Nueva Sesión": nueva_sesion_ui,
        "Sesiones Guardadas": sesiones_guardadas_tab,
        "Tabla de Resumen": tabla_resumen_ui,
        "Evaluaciones": evaluaciones_ui
    }
    
    opcion = st.sidebar.radio("Selecciona una opción", list(menu_options.keys()))
    menu_options[opcion](st.session_state.db)

if __name__ == "__main__":
    main()