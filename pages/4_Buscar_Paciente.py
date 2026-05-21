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
            .select("id_pacientes, nombre, apellido, habitacion, diagnostico") \
            .eq("nombre", nombre) \
            .eq("apellido", apellido) \
            .execute()
        return response.data if response.data else None
    except Exception as e:
        st.error(f"Error al buscar el paciente: {e}")
        return None


def buscar_id_paciente_page():
    st.title("Buscar Paciente")

    nombre   = st.text_input("Nombre del Paciente",   key="nombre_paciente")
    apellido = st.text_input("Apellido del Paciente",  key="apellido_paciente")

    if st.button("Buscar", key="btn_buscar_id"):
        if nombre and apellido:
            pacientes = buscar_id_paciente(nombre, apellido)
            if pacientes:
                if len(pacientes) == 1:
                    p = pacientes[0]
                    st.success(f"Paciente encontrado — ID: **{p['id_pacientes']}**")
                    st.write(f"**Habitación:** {p['habitacion']}")
                    st.write(f"**Diagnóstico:** {p['diagnostico']}")
                else:
                    st.warning("Se encontraron múltiples pacientes con ese nombre y apellido:")
                    for p in pacientes:
                        st.write(f"- ID: **{p['id_pacientes']}** | Habitación: {p['habitacion']} | Diagnóstico: {p['diagnostico']}")
            else:
                st.warning("No se encontró ningún paciente con ese nombre y apellido.")
        else:
            st.error("Por favor, complete ambos campos.")


if 'estado' not in st.session_state:
    st.session_state['estado'] = 'No Autorizado'

if st.session_state['estado'] == 'Autorizado':
    buscar_id_paciente_page()
else:
    st.title("Acceso Restringido")
    st.error("Debes iniciar sesión primero.")