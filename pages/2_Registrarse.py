import streamlit as st
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client import db

favicon = "https://github.com/soutovicky/Meditrack2/blob/main/Imagenes/Icon.png?raw=true"
st.set_page_config(page_title='Meditrack', page_icon=favicon, layout='wide')


def show_loading_bar():
    with st.spinner('Registrando usuario...'):
        progress_bar = st.progress(0)
        for percent_complete in range(100):
            time.sleep(0.02)
            progress_bar.progress(percent_complete + 1)


def registrar_empleado(id_empleado, nombre, apellido, cargo, sector_hospitalario, horario_entrada, horario_salida, email, contraseña):
    try:
        db().table("empleado").insert({
            "id_empleado":         id_empleado,
            "nombre":              nombre,
            "apellido":            apellido,
            "cargo":               cargo,
            "sector_hospitalario": sector_hospitalario,
            "horario_entrada":     str(horario_entrada),
            "horario_salida":      str(horario_salida),
            "email":               email,
            "contraseña":          contraseña
        }).execute()
        return True
    except Exception as e:
        st.error(f"Error al registrar empleado: {e}")
        return False


def registrar_doctor(id_doctor, nombre, apellido, especialidad, hospital, email, contraseña):
    try:
        db().table("doctor").insert({
            "id_doctor":   id_doctor,
            "nombre":      nombre,
            "apellido":    apellido,
            "especialidad":especialidad,
            "hospital":    hospital,
            "email":       email,
            "contraseña":  contraseña
        }).execute()
        return True
    except Exception as e:
        st.error(f"Error al registrar doctor: {e}")
        return False


def main():
    st.title("Registrar usuario")

    nombre_input    = st.text_input("Nombre:")
    apellido_input  = st.text_input("Apellido:")
    email_input     = st.text_input("Email institucional:")
    contraseña_input = st.text_input("Contraseña:", type="password")
    ocupacion_input = st.selectbox("Ocupación:", ["Empleado", "Doctor"])

    if ocupacion_input == "Empleado":
        id_empleado_input        = st.text_input("ID del Empleado:", placeholder="Ej: EMP001")
        cargo_input              = st.selectbox("Cargo:", ["Enfermero/a", "Auxiliar de Enfermería", "Jefe/a de Enfermería", "Administrativo/a", "Técnico/a"])
        sector_hospitalario_input = st.selectbox("Sector Hospitalario:", [
            "Clínica Médica", "Cardiología", "Neurología", "Traumatología",
            "Cirugía", "Oncología", "Infectología", "Hematología",
            "Endocrinología", "Nefrología", "Gastroenterología",
            "Psiquiatría", "Guardia", "Administración", "Farmacia"
        ])
        horario_entrada_input = st.time_input("Horario de Entrada:")
        horario_salida_input  = st.time_input("Horario de Salida:")

        if st.button("Registrarse como Empleado"):
            show_loading_bar()
            if not nombre_input or not apellido_input or not id_empleado_input:
                st.error("Por favor, complete los campos obligatorios.")
            elif registrar_empleado(id_empleado_input, nombre_input, apellido_input, cargo_input, sector_hospitalario_input, horario_entrada_input, horario_salida_input, email_input, contraseña_input):
                st.success("Empleado registrado exitosamente. Ya puede iniciar sesión.")
                st.page_link("pages/1_Iniciar_Sesión.py", label="Ir a Iniciar Sesión", icon="➡️")
            else:
                st.error("Error al registrar empleado.")

    elif ocupacion_input == "Doctor":
        id_doctor_input    = st.text_input("ID del Doctor:", placeholder="Ej: DOC001")
        especialidad_input = st.selectbox("Especialidad:", [
            "Clínica Médica", "Cardiología", "Neurología", "Traumatología",
            "Cirugía General", "Oncología", "Infectología", "Hematología",
            "Endocrinología", "Nefrología", "Gastroenterología",
            "Psiquiatría", "Neumología", "Reumatología", "Dermatología",
            "Medicina Interna", "Cirugía Cardiovascular", "Urología"
        ])
        hospital_input = st.text_input("Hospital / Institución:")

        if st.button("Registrarse como Doctor"):
            show_loading_bar()
            if not nombre_input or not apellido_input or not id_doctor_input:
                st.error("Por favor, complete los campos obligatorios.")
            elif registrar_doctor(id_doctor_input, nombre_input, apellido_input, especialidad_input, hospital_input, email_input, contraseña_input):
                st.success("Doctor registrado exitosamente. Ya puede iniciar sesión.")
                st.page_link("pages/1_Iniciar_Sesión.py", label="Ir a Iniciar Sesión", icon="➡️")
            else:
                st.error("Error al registrar doctor.")


if __name__ == "__main__":
    main()