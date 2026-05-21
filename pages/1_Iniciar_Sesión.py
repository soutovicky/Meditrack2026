import streamlit as st
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client import db

favicon = "https://github.com/soutovicky/Meditrack2/blob/main/Imagenes/Icon.png?raw=true"
st.set_page_config(page_title='Meditrack', page_icon=favicon, layout='wide')


def show_loading_bar():
    with st.spinner('Tus datos se están registrando...'):
        progress_bar = st.progress(0)
        for percent_complete in range(100):
            time.sleep(0.05)
            progress_bar.progress(percent_complete + 1)


def check_id_in_empleado(id_to_check):
    try:
        response = db().table("empleado") \
            .select("id_empleado, nombre, apellido") \
            .eq("id_empleado", id_to_check) \
            .execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"Error al consultar empleado: {e}")
        return None


def check_id_in_doctor(id_to_check):
    try:
        response = db().table("doctor") \
            .select("id_doctor, nombre, apellido") \
            .eq("id_doctor", id_to_check) \
            .execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"Error al consultar doctores: {e}")
        return None


def update_user_details(id, nombre, apellido, table):
    try:
        if table == 'empleado':
            db().table("empleado") \
                .update({"nombre": nombre, "apellido": apellido}) \
                .eq("id_empleado", id) \
                .execute()
        else:
            db().table("doctor") \
                .update({"nombre": nombre, "apellido": apellido}) \
                .eq("id_doctor", id) \
                .execute()
    except Exception as e:
        st.error(f"Error al actualizar los detalles: {e}")


# Interfaz
st.title("Iniciar Sesión")

id_input = st.text_input("ID de Empleado o Doctor:", type="password", key="perfil_paciente_id")
nombre_input = st.text_input("Ingrese su Nombre:")
apellido_input = st.text_input("Ingrese su Apellido:")

if 'estado' not in st.session_state:
    st.session_state['estado'] = 'No Autorizado'
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None

if st.button("Iniciar Sesion"):
    show_loading_bar()
    if not id_input or not nombre_input or not apellido_input:
        st.error("Por favor, complete todos los campos.")
    else:
        empleado_details = check_id_in_empleado(id_input)
        doctor_details = check_id_in_doctor(id_input)

        if empleado_details:
            update_user_details(id_input, nombre_input, apellido_input, 'empleado')
            st.session_state['user_id'] = id_input
            st.success("Inicio de sesión exitoso")
            st.write("¡Ahora puede ver novedades del Geriátrico en la página de Bienvenidos!")
            st.session_state['estado'] = 'Autorizado'
            st.session_state['user_role'] = 'Empleado'
            st.page_link("pages/3_Mi_Perfil.py", label="Mi Perfil", icon="➡️")
            st.page_link("Bienvenidos.py", label="Volver al Inicio", icon="➡️")

        elif doctor_details:
            update_user_details(id_input, nombre_input, apellido_input, 'doctor')
            st.session_state['user_id'] = id_input
            st.success("Inicio de sesión exitoso")
            st.write("¡Ahora puede ver novedades del Geriátrico en la página de Bienvenidos!")
            st.session_state['estado'] = 'Autorizado'
            st.session_state['user_role'] = 'Doctor'
            st.page_link("pages/3_Mi_Perfil.py", label="Mi Perfil", icon="➡️")
            st.page_link("Bienvenidos.py", label="Volver al Inicio", icon="➡️")

        else:
            st.error("El ID no existe en la base de datos.")