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


def registrar_empleado(id_empleado, nombre, apellido, sector_hospitalario, horario_entrada, horario_salida):
    try:
        db().table("empleado").insert({
            "id_empleado": id_empleado,
            "nombre": nombre,
            "apellido": apellido,
            "sector_hospitalario": sector_hospitalario,
            "horario_entrada": str(horario_entrada),
            "horario_salida": str(horario_salida)
        }).execute()
        return True
    except Exception as e:
        st.error(f"Error al registrar empleado: {e}")
        return False


def registrar_doctor(id_doctor, nombre, apellido, hospital):
    try:
        db().table("doctor").insert({
            "id_doctor": id_doctor,
            "nombre": nombre,
            "apellido": apellido,
            "hospital": hospital
        }).execute()
        return True
    except Exception as e:
        st.error(f"Error al registrar doctor: {e}")
        return False


def main():
    st.title("Registrar usuario")

    nombre_input = st.text_input("Ingrese su Nombre:")
    apellido_input = st.text_input("Ingrese su Apellido:")
    ocupacion_input = st.selectbox("Seleccione su Ocupación:", ["Empleado", "Doctor"])

    if ocupacion_input == "Empleado":
        id_empleado_input = st.text_input("ID del Empleado:", placeholder="Ej: EMP00000")
        sector_hospitalario_input = st.text_input("Sector Hospitalario:")
        horario_entrada_input = st.time_input("Horario de Entrada:")
        horario_salida_input = st.time_input("Horario de Salida:")

        if st.button("Registrarse como Empleado"):
            show_loading_bar()
            if registrar_empleado(id_empleado_input, nombre_input, apellido_input, sector_hospitalario_input, horario_entrada_input, horario_salida_input):
                st.success("Empleado registrado exitosamente. Ahora puede iniciar sesión")
                st.page_link("pages/1_Iniciar_Sesión.py", label="Inicio", icon="➡️")
            else:
                st.error("Error al registrar empleado")

    elif ocupacion_input == "Doctor":
        id_doctor_input = st.text_input("ID del Doctor:", placeholder="Ej: 45072248")
        hospital_input = st.text_input("Hospital:")

        if st.button("Registrarse como Doctor"):
            show_loading_bar()
            if registrar_doctor(id_doctor_input, nombre_input, apellido_input, hospital_input):
                st.success("Doctor registrado exitosamente. Ahora puede iniciar sesión")
                st.page_link("pages/1_Iniciar_Sesión.py", label="Inicio", icon="➡️")
            else:
                st.error("Error al registrar doctor")


if __name__ == "__main__":
    main()