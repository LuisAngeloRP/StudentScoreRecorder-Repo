import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

class SupabaseManager:
    def __init__(self):
        self.supabase_url = st.secrets["supabase_url"]
        self.supabase_key = st.secrets["supabase_key"]
        self.client = create_client(self.supabase_url, self.supabase_key)
        self._verificar_tablas()

    def _verificar_tablas(self):
        """Verifica y crea las tablas necesarias si no existen"""
        try:
            response = self.client.table('cursos').select('*').execute()
            if not response.data:
                self.client.table('cursos').insert({
                    'nombre': 'Curso de Ejemplo',
                    'codigo': 'CURSO101'
                }).execute()
        except Exception as e:
            st.error(f"Error al verificar tablas: {str(e)}")

    def crear_sesion(self, codigo_curso: str, nombre: str, puntaje_maximo: int, fecha) -> int:
        """
        Crea una nueva sesión
        Retorna el ID de la sesión creada o None si hay error
        """
        try:
            # Obtener ID del curso
            curso = self.client.table('cursos')\
                .select('id')\
                .eq('codigo', codigo_curso)\
                .single()\
                .execute()
            
            if not curso.data:
                st.error(f"No se encontró el curso con código {codigo_curso}")
                return None
            
            # Crear la sesión
            response = self.client.table('sesiones').insert({
                'curso_id': curso.data['id'],
                'nombre': nombre,
                'puntaje_maximo': puntaje_maximo,
                'fecha': fecha.strftime('%Y-%m-%d')
            }).execute()
            
            if response.data:
                return response.data[0]['id']
            return None
            
        except Exception as e:
            st.error(f"Error al crear sesión: {str(e)}")
            return None

    def actualizar_puntaje_en_sesion(self, sesion_id: int, apellido: str, nombre: str, puntaje: int) -> bool:
        """
        Actualiza el puntaje de un alumno en una sesión específica
        """
        try:
            # Obtener ID del alumno
            alumno = self.client.table('alumnos')\
                .select('id')\
                .eq('apellido', apellido)\
                .eq('nombre', nombre)\
                .single()\
                .execute()
            
            if not alumno.data:
                return False
                
            # Verificar si ya existe un puntaje para este alumno en esta sesión
            puntaje_existente = self.client.table('puntajes')\
                .select('id')\
                .eq('sesion_id', sesion_id)\
                .eq('alumno_id', alumno.data['id'])\
                .execute()
                
            if puntaje_existente.data:
                # Actualizar puntaje existente
                self.client.table('puntajes')\
                    .update({'puntaje': puntaje})\
                    .eq('id', puntaje_existente.data[0]['id'])\
                    .execute()
            else:
                # Crear nuevo puntaje
                self.client.table('puntajes').insert({
                    'sesion_id': sesion_id,
                    'alumno_id': alumno.data['id'],
                    'puntaje': puntaje
                }).execute()
                
            return True
            
        except Exception as e:
            print(f"Error al actualizar puntaje: {str(e)}")
            return False

    def actualizar_puntaje_alumno(self, codigo_curso: str, alumno_apellido: str, alumno_nombre: str, puntaje: int) -> bool:
        """
        Actualiza el puntaje de un alumno en la sesión actual
        """
        try:
            # Obtener ID del curso
            curso = self.client.table('cursos')\
                .select('id')\
                .eq('codigo', codigo_curso)\
                .single()\
                .execute()
            
            if not curso.data:
                return False
            
            # Obtener ID del alumno
            alumno = self.client.table('alumnos')\
                .select('id')\
                .eq('curso_id', curso.data['id'])\
                .eq('apellido', alumno_apellido)\
                .eq('nombre', alumno_nombre)\
                .single()\
                .execute()
            
            if not alumno.data:
                return False
            
            # Verificar si existe una sesión actual
            sesion_actual = self.client.table('sesiones')\
                .select('id')\
                .eq('curso_id', curso.data['id'])\
                .eq('fecha', datetime.now().strftime('%Y-%m-%d'))\
                .single()\
                .execute()
            
            # Si no existe sesión actual, crearla
            if not sesion_actual.data:
                sesion = self.client.table('sesiones').insert({
                    'curso_id': curso.data['id'],
                    'nombre': f'Sesión {datetime.now().strftime("%Y-%m-%d")}',
                    'fecha': datetime.now().strftime('%Y-%m-%d'),
                    'puntaje_maximo': 20  # Valor por defecto
                }).execute()
                sesion_id = sesion.data[0]['id']
            else:
                sesion_id = sesion_actual.data['id']
            
            # Actualizar o crear puntaje
            puntaje_existente = self.client.table('puntajes')\
                .select('id')\
                .eq('sesion_id', sesion_id)\
                .eq('alumno_id', alumno.data['id'])\
                .single()\
                .execute()
            
            if puntaje_existente.data:
                # Actualizar puntaje existente
                self.client.table('puntajes')\
                    .update({'puntaje': puntaje})\
                    .eq('id', puntaje_existente.data['id'])\
                    .execute()
            else:
                # Crear nuevo puntaje
                self.client.table('puntajes').insert({
                    'sesion_id': sesion_id,
                    'alumno_id': alumno.data['id'],
                    'puntaje': puntaje
                }).execute()
            
            return True
            
        except Exception as e:
            print(f"Error al actualizar puntaje: {str(e)}")
            return False

    def _verificar_tablas(self):
        """Verifica y crea las tablas necesarias si no existen"""
        try:
            response = self.client.table('cursos').select('*').execute()
            if not response.data:
                self.client.table('cursos').insert({
                    'nombre': 'Curso de Ejemplo',
                    'codigo': 'CURSO101'
                }).execute()
        except Exception as e:
            st.error(f"Error al verificar tablas: {str(e)}")

    def obtener_lista_cursos(self):
        """Obtiene la lista de cursos disponibles"""
        try:
            response = self.client.table('cursos').select('codigo, nombre').execute()
            if not response.data:
                return [], []
            df = pd.DataFrame(response.data)
            return df['codigo'].tolist(), df['nombre'].tolist()
        except Exception as e:
            st.error(f"Error al obtener lista de cursos: {str(e)}")
            return [], []

    def crear_curso(self, nombre, codigo):
        """Crea un nuevo curso"""
        try:
            # Primero verificar si el curso ya existe
            curso_existente = self.client.table('cursos')\
                .select('*')\
                .eq('codigo', codigo.strip())\
                .execute()
            
            if curso_existente.data:
                st.error(f"Ya existe un curso con el código {codigo}")
                return False
            
            # Crear el nuevo curso
            response = self.client.table('cursos')\
                .insert({
                    'nombre': nombre.strip(),
                    'codigo': codigo.strip()
                })\
                .execute()
            
            if not response.data:
                st.error("No se pudo crear el curso. Respuesta vacía del servidor.")
                return False
            
            return True
            
        except Exception as e:
            st.error(f"Error al crear curso: {str(e)}")
            return False

    def leer_alumnos_curso(self, codigo_curso):
        """Lee la lista de alumnos de un curso específico"""
        try:
            # Primero obtener el ID del curso
            curso = self.client.table('cursos')\
                .select('id')\
                .eq('codigo', codigo_curso)\
                .single()\
                .execute()
            
            if not curso.data:
                st.error(f"No se encontró el curso con código {codigo_curso}")
                return pd.DataFrame(columns=['Apellido', 'Nombre', 'Puntaje'])
            
            # Obtener los alumnos del curso
            response = self.client.table('alumnos')\
                .select('apellido, nombre')\
                .eq('curso_id', curso.data['id'])\
                .order('apellido')\
                .execute()
            
            if not response.data:
                return pd.DataFrame(columns=['Apellido', 'Nombre', 'Puntaje'])
            
            # Crear DataFrame con los datos
            df = pd.DataFrame(response.data)
            df.columns = ['Apellido', 'Nombre']
            df['Puntaje'] = 0
            
            return df
            
        except Exception as e:
            st.error(f"Error al leer alumnos del curso: {str(e)}")
            return pd.DataFrame(columns=['Apellido', 'Nombre', 'Puntaje'])

    def agregar_alumno(self, codigo_curso, apellido, nombre):
        """Agrega un nuevo alumno al curso"""
        try:
            # Obtener ID del curso
            curso = self.client.table('cursos')\
                .select('id')\
                .eq('codigo', codigo_curso.strip())\
                .single()\
                .execute()
            
            if not curso.data:
                st.error(f"No se encontró el curso con código {codigo_curso}")
                return False
            
            # Verificar si el alumno ya existe
            alumno_existente = self.client.table('alumnos')\
                .select('id')\
                .eq('curso_id', curso.data['id'])\
                .eq('apellido', apellido.strip())\
                .eq('nombre', nombre.strip())\
                .execute()
            
            if alumno_existente.data:
                st.warning(f"El alumno {apellido}, {nombre} ya existe en este curso")
                return False
            
            # Insertar nuevo alumno
            response = self.client.table('alumnos')\
                .insert({
                    'curso_id': curso.data['id'],
                    'apellido': apellido.strip(),
                    'nombre': nombre.strip()
                })\
                .execute()
            
            if not response.data:
                st.error(f"No se pudo agregar al alumno {apellido}, {nombre}")
                return False
            
            return True
            
        except Exception as e:
            st.error(f"Error al agregar alumno: {str(e)}")
            return False

    def guardar_sesion(self, codigo_curso, nombre_sesion, puntaje_maximo, fecha, df_alumnos):
        """Guarda una nueva sesión con sus puntajes"""
        try:
            # Obtener ID del curso
            curso = self.client.table('cursos')\
                .select('id')\
                .eq('codigo', codigo_curso)\
                .single()\
                .execute()
            
            if not curso.data:
                st.error(f"No se encontró el curso con código {codigo_curso}")
                return None
            
            # Crear la sesión
            sesion = self.client.table('sesiones').insert({
                'curso_id': curso.data['id'],
                'nombre': nombre_sesion,
                'puntaje_maximo': puntaje_maximo,
                'fecha': fecha.strftime('%Y-%m-%d')
            }).execute()
            
            sesion_id = sesion.data[0]['id']
            
            # Guardar puntajes de cada alumno
            for _, row in df_alumnos.iterrows():
                # Obtener ID del alumno
                alumno = self.client.table('alumnos')\
                    .select('id')\
                    .eq('curso_id', curso.data['id'])\
                    .eq('apellido', row['Apellido'])\
                    .eq('nombre', row['Nombre'])\
                    .single()\
                    .execute()
                
                if alumno.data:
                    # Guardar puntaje
                    self.client.table('puntajes').insert({
                        'sesion_id': sesion_id,
                        'alumno_id': alumno.data['id'],
                        'puntaje': row['Puntaje']
                    }).execute()
            
            return sesion_id
            
        except Exception as e:
            st.error(f"Error al guardar sesión: {str(e)}")
            return None

    def obtener_sesiones_curso(self, codigo_curso):
        """Obtiene todas las sesiones de un curso"""
        try:
            # Obtener ID del curso
            curso = self.client.table('cursos')\
                .select('id')\
                .eq('codigo', codigo_curso)\
                .single()\
                .execute()
            
            if not curso.data:
                return pd.DataFrame()
            
            # Obtener sesiones
            response = self.client.table('sesiones')\
                .select('id, nombre, puntaje_maximo, fecha')\
                .eq('curso_id', curso.data['id'])\
                .order('fecha')\
                .execute()
            
            return pd.DataFrame(response.data)
            
        except Exception as e:
            st.error(f"Error al obtener sesiones: {str(e)}")
            return pd.DataFrame()

    def obtener_puntajes_sesion(self, sesion_id):
        """Obtiene los puntajes de una sesión específica"""
        try:
            response = self.client.table('puntajes')\
                .select('alumnos(apellido, nombre), puntaje')\
                .eq('sesion_id', sesion_id)\
                .execute()
            
            if not response.data:
                return pd.DataFrame(columns=['Apellido', 'Nombre', 'Puntaje'])
            
            # Procesar los datos anidados
            data = []
            for row in response.data:
                data.append({
                    'Apellido': row['alumnos']['apellido'],
                    'Nombre': row['alumnos']['nombre'],
                    'Puntaje': row['puntaje']
                })
            
            return pd.DataFrame(data)
            
        except Exception as e:
            st.error(f"Error al obtener puntajes: {str(e)}")
            return pd.DataFrame(columns=['Apellido', 'Nombre', 'Puntaje'])

    def actualizar_puntajes_sesion(self, sesion_id, df_puntajes):
        """Actualiza los puntajes de una sesión"""
        try:
            for _, row in df_puntajes.iterrows():
                # Obtener ID del alumno
                alumno = self.client.table('alumnos')\
                    .select('id')\
                    .eq('apellido', row['Apellido'])\
                    .eq('nombre', row['Nombre'])\
                    .single()\
                    .execute()
                
                if alumno.data:
                    # Actualizar puntaje
                    self.client.table('puntajes')\
                        .update({'puntaje': row['Puntaje']})\
                        .eq('sesion_id', sesion_id)\
                        .eq('alumno_id', alumno.data['id'])\
                        .execute()
            
            return True
            
        except Exception as e:
            st.error(f"Error al actualizar puntajes: {str(e)}")
            return False
    def obtener_evaluaciones_curso(self, codigo_curso):
        """Obtiene todas las evaluaciones de un curso"""
        try:
            # Obtener ID del curso
            curso = self.client.table('cursos')\
                .select('id')\
                .eq('codigo', codigo_curso)\
                .single()\
                .execute()
            
            if not curso.data:
                return []
            
            # Obtener evaluaciones
            response = self.client.table('evaluaciones')\
                .select('*')\
                .eq('curso_id', curso.data['id'])\
                .order('fecha')\
                .execute()
            
            evaluaciones = []
            for eval_data in response.data:
                # Obtener sesiones asociadas
                sesiones = self.client.table('evaluaciones_sesiones')\
                    .select('sesiones(nombre, fecha, puntaje_maximo)')\
                    .eq('evaluacion_id', eval_data['id'])\
                    .execute()
                
                sesiones_info = [
                    {
                        'nombre': s['sesiones']['nombre'],
                        'fecha': s['sesiones']['fecha'],
                        'puntaje_maximo': s['sesiones']['puntaje_maximo']
                    } for s in sesiones.data
                ]
                
                evaluaciones.append({
                    'id': eval_data['id'],
                    'nombre': eval_data['nombre'],
                    'escala': eval_data['escala'],
                    'fecha': eval_data['fecha'],
                    'sesiones': sesiones_info
                })
            
            return evaluaciones
        except Exception as e:
            st.error(f"Error al obtener evaluaciones: {str(e)}")
            return []

    def obtener_sesion(self, sesion_id):
        """Obtiene los detalles de una sesión específica"""
        try:
            response = self.client.table('sesiones')\
                .select('*')\
                .eq('id', sesion_id)\
                .single()\
                .execute()
            
            return response.data
        except Exception as e:
            st.error(f"Error al obtener sesión: {str(e)}")
            return None

    def obtener_resultados_evaluacion(self, evaluacion_id):
        """Obtiene los resultados detallados de una evaluación"""
        try:
            # Obtener la evaluación
            evaluacion = self.client.table('evaluaciones')\
                .select('*')\
                .eq('id', evaluacion_id)\
                .single()\
                .execute()
            
            if not evaluacion.data:
                return None

            # Obtener las sesiones asociadas
            sesiones = self.client.table('evaluaciones_sesiones')\
                .select('sesion_id')\
                .eq('evaluacion_id', evaluacion_id)\
                .execute()
            
            sesiones_ids = [s['sesion_id'] for s in sesiones.data]
            
            # Obtener los alumnos del curso
            alumnos = self.client.table('alumnos')\
                .select('id, apellido, nombre')\
                .eq('curso_id', evaluacion.data['curso_id'])\
                .execute()
            
            resultados = []
            for alumno in alumnos.data:
                puntaje_total = 0
                puntaje_maximo = 0
                
                # Calcular puntajes para cada sesión
                for sesion_id in sesiones_ids:
                    sesion = self.obtener_sesion(sesion_id)
                    if sesion:
                        puntaje_maximo += sesion['puntaje_maximo']
                        
                        # Obtener puntaje del alumno
                        puntaje = self.client.table('puntajes')\
                            .select('puntaje')\
                            .eq('sesion_id', sesion_id)\
                            .eq('alumno_id', alumno['id'])\
                            .single()\
                            .execute()
                        
                        if puntaje.data:
                            puntaje_total += puntaje.data['puntaje']
                
                # Calcular nota final
                porcentaje = (puntaje_total / puntaje_maximo * 100) if puntaje_maximo > 0 else 0
                nota = round((porcentaje * evaluacion.data['escala']) / 100, 2)
                
                resultados.append({
                    'Apellido': alumno['apellido'],
                    'Nombre': alumno['nombre'],
                    'Puntaje Total': puntaje_total,
                    'Puntaje Máximo': puntaje_maximo,
                    'Porcentaje': round(porcentaje, 2),
                    'Nota': nota
                })
            
            return pd.DataFrame(resultados)
            
        except Exception as e:
            st.error(f"Error al obtener resultados de evaluación: {str(e)}")
            return None

    def crear_evaluacion(self, codigo_curso, nombre_evaluacion, escala, sesiones_ids, fecha=None):
        """Crea una nueva evaluación"""
        try:
            # Obtener ID del curso
            curso = self.client.table('cursos')\
                .select('id')\
                .eq('codigo', codigo_curso)\
                .single()\
                .execute()
            
            if not curso.data:
                st.error(f"No se encontró el curso con código {codigo_curso}")
                return None
            
            # Crear la evaluación
            if fecha is None:
                fecha = datetime.now()
                
            evaluacion = self.client.table('evaluaciones').insert({
                'curso_id': curso.data['id'],
                'nombre': nombre_evaluacion,
                'escala': escala,
                'fecha': fecha.strftime('%Y-%m-%d')
            }).execute()
            
            evaluacion_id = evaluacion.data[0]['id']
            
            # Relacionar con sesiones
            for sesion_id in sesiones_ids:
                self.client.table('evaluaciones_sesiones').insert({
                    'evaluacion_id': evaluacion_id,
                    'sesion_id': sesion_id
                }).execute()
            
            return evaluacion_id
            
        except Exception as e:
            st.error(f"Error al crear evaluación: {str(e)}")
            return None

    def eliminar_evaluacion(self, evaluacion_id):
        """Elimina una evaluación y sus relaciones"""
        try:
            # Primero eliminar las relaciones con sesiones
            self.client.table('evaluaciones_sesiones')\
                .delete()\
                .eq('evaluacion_id', evaluacion_id)\
                .execute()
            
            # Luego eliminar la evaluación
            self.client.table('evaluaciones')\
                .delete()\
                .eq('id', evaluacion_id)\
                .execute()
            
            return True
            
        except Exception as e:
            st.error(f"Error al eliminar evaluación: {str(e)}")
            return False
    
    