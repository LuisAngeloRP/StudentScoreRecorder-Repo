import streamlit as st

import streamlit as st
import pandas as pd


def validar_puntaje_maximo(df: pd.DataFrame, puntaje_maximo: int) -> bool:
    """Valida que ningún puntaje exceda el máximo permitido"""
    if df['puntaje'].max() > puntaje_maximo:
        st.error(f"Error: Algunos puntajes exceden el máximo permitido ({puntaje_maximo})")
        return False
    return True

def validar_nombre_sesion(nombre):
    """Valida que el nombre de la sesión sea válido"""
    if not nombre or len(nombre.strip()) == 0:
        st.error("El nombre de la sesión no puede estar vacío")
        return False
    return True

def validar_fecha(fecha):
    """Valida que la fecha sea válida"""
    if not fecha:
        st.error("Debe seleccionar una fecha válida")
        return False
    return True

def validar_evaluacion(nombre, escala, sesiones_seleccionadas):
    """Valida los datos de una evaluación"""
    if not nombre or len(nombre.strip()) == 0:
        st.error("El nombre de la evaluación no puede estar vacío")
        return False
        
    if escala <= 0:
        st.error("La escala debe ser mayor a 0")
        return False
        
    if not sesiones_seleccionadas:
        st.error("Debe seleccionar al menos una sesión")
        return False
        
    return True

def validar_fecha_evaluacion(fecha):
    """Valida que la fecha de evaluación sea válida"""
    if not fecha:
        st.error("Debe seleccionar una fecha válida")
        return False
        
    return True

def calcular_nota_final(puntaje_total, puntaje_maximo, escala):
    """Calcula la nota final según la escala"""
    if puntaje_maximo == 0:
        return 0
    porcentaje = (puntaje_total / puntaje_maximo) * 100
    return round((porcentaje * escala) / 100, 2)

def generar_reporte_evaluacion(df_resultados):
    """Genera estadísticas del reporte de evaluación"""
    return {
        'promedio': df_resultados['Nota'].mean(),
        'mediana': df_resultados['Nota'].median(),
        'max': df_resultados['Nota'].max(),
        'min': df_resultados['Nota'].min(),
        'aprobados': len(df_resultados[df_resultados['Nota'] >= 11]),
        'desaprobados': len(df_resultados[df_resultados['Nota'] < 11]),
        'total_alumnos': len(df_resultados)
    }

