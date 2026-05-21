import streamlit as st
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client import db

favicon = "https://github.com/soutovicky/Meditrack2/blob/main/Imagenes/Icon.png?raw=true"
st.set_page_config(page_title='Meditrack', page_icon=favicon, layout='wide')


def show_loading_bar():
    with st.spinner('Verificando credenciales...'):
        progress_bar = st.progress(0)
        for percent_complete in range(100):
            time.sleep(0.02)
            progress_bar.progress(percent_complete + 1)


def check_empleado(id_to_check, nombre, apellido, contraseña):
    try:
        response = db().table("empleado") \
            .select("id_empleado, nombre, apellido, contraseña") \
            .eq("id_empleado", id_to_check) \
            .execute()

        if not response.data:
            return None, "id_not_found"

        empleado = response.data[0]

        if empleado["nombre"].strip().lower() != nombre.strip().lower() or \
           empleado["apellido"].strip().lower() != apellido.strip().lower():
            return None, "wrong_name"

        if empleado["contraseña"] != contraseña:
            return None, "wrong_password"

        return empleado, "ok"
    except Exception as e:
        st.error(f"Error al consultar empleado: {e}")
        return None, "error"


def check_doctor(id_to_check, nombre, apellido, contraseña):
    try:
        response = db().table("doctor") \
            .select("id_doctor, nombre, apellido, contraseña") \
            .eq("id_doctor", id_to_check) \
            .execute()

        if not response.data:
            return None, "id_not_found"

        doctor = response.data[0]

        if doctor["nombre"].strip().lower() != nombre.strip().lower() or \
           doctor["apellido"].strip().lower() != apellido.strip().lower():
            return None, "wrong_name"

        if doctor["contraseña"] != contraseña:
            return None, "wrong_password"

        return doctor, "ok"
    except Exception as e:
        st.error(f"Error al consultar doctor: {e}")
        return None, "error"


# Interfaz
st.title("Iniciar Sesión")

id_input         = st.text_input("ID de Empleado o Doctor:", key="login_id_input")
nombre_input     = st.text_input("Nombre:", key="login_nombre_input")
apellido_input   = st.text_input("Apellido:", key="login_apellido_input")
contraseña_input = st.text_input("Contraseña:", type="password", key="login_pass_input")

if 'estado' not in st.session_state:
    st.session_state['estado'] = 'No Autorizado'
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None

if st.button("Iniciar Sesión"):
    if not id_input or not nombre_input or not apellido_input or not contraseña_input:
        st.error("Por favor, complete todos los campos.")
    else:
        show_loading_bar()

        empleado, estado_emp = check_empleado(id_input, nombre_input, apellido_input, contraseña_input)
        doctor,   estado_doc = check_doctor(id_input, nombre_input, apellido_input, contraseña_input)

        if empleado and estado_emp == "ok":
            st.session_state['user_id']   = id_input
            st.session_state['estado']    = 'Autorizado'
            st.session_state['user_role'] = 'Empleado'
            st.success(f"¡Bienvenido/a, {empleado['nombre']} {empleado['apellido']}!")
            st.page_link("pages/3_Mi_Perfil.py", label="Ir a mi Perfil", icon="➡️")
            st.page_link("Bienvenidos.py",        label="Volver al Inicio", icon="🏠")

        elif doctor and estado_doc == "ok":
            st.session_state['user_id']   = id_input
            st.session_state['estado']    = 'Autorizado'
            st.session_state['user_role'] = 'Doctor'
            st.success(f"¡Bienvenido/a, Dr/a. {doctor['nombre']} {doctor['apellido']}!")
            st.page_link("pages/3_Mi_Perfil.py", label="Ir a mi Perfil", icon="➡️")
            st.page_link("Bienvenidos.py",        label="Volver al Inicio", icon="🏠")

        elif estado_emp == "wrong_password" or estado_doc == "wrong_password":
            st.error("❌ Contraseña incorrecta.")

        elif estado_emp == "wrong_name" or estado_doc == "wrong_name":
            st.error("❌ El nombre o apellido no coincide con el ID ingresado.")

        else:
            st.error("❌ El ID no existe en la base de datos.")