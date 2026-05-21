import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client import db

favicon = "https://github.com/soutovicky/Meditrack2/blob/main/Imagenes/Icon.png?raw=true"
st.set_page_config(page_title='Meditrack', page_icon=favicon, layout='wide')


def buscar_id_paciente(nombre, apellido):
    try:
        response = db().table("pacientes") \
            .select("id_pacientes, nombre, apellido") \
            .eq("nombre", nombre) \
            .eq("apellido", apellido) \
            .execute()
        return response.data if response.data else None
    except Exception as e:
        st.error(f"Error al buscar el ID del paciente: {e}")
        return None


def buscar_id_paciente_page():
    st.title("Buscar ID de Paciente")

    nombre = st.text_input("Nombre del Paciente", key="nombre_paciente")
    apellido = st.text_input("Apellido del Paciente", key="apellido_paciente")

    if st.button("Buscar ID", key="btn_buscar_id"):
        if nombre and apellido:
            pacientes = buscar_id_paciente(nombre, apellido)
            if pacientes:
                if len(pacientes) == 1:
                    st.success(f"ID del Paciente: {pacientes[0]['id_pacientes']}")
                else:
                    st.warning("Se encontraron múltiples pacientes con el mismo nombre y apellido.")
                    for p in pacientes:
                        st.write(f"ID: {p['id_pacientes']}, Nombre: {p['nombre']}, Apellido: {p['apellido']}")
            else:
                st.warning("No se encontró ningún paciente con ese nombre y apellido.")
        else:
            st.error("Por favor, complete ambos campos.")


# Inicializar sesión
if 'estado' not in st.session_state:
    st.session_state['estado'] = 'No Autorizado'
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None

if st.session_state['estado'] == 'Autorizado':
    buscar_id_paciente_page()
else:
    st.title("Usted aún no puede buscar un Paciente")
    st.error("Debes iniciar sesión primero.")