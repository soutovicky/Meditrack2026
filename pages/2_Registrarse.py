import streamlit as st
import psycopg2
import random
import time

# Configuración de la página con favicon
favicon = "https://github.com/soutovicky/Meditrack2/blob/main/Imagenes/Icon.png?raw=true"
st.set_page_config(page_title='Meditrack', page_icon=favicon,layout='wide')


# Configuración de la conexión a la base de datos
def get_db_connection():
    try:
        user = 'postgres.xqfolwxwquynnugqmrnw'
        password = 'Meditrack2024'
        host = 'aws-0-us-west-1.pooler.supabase.com'
        port = '5432'
        dbname = 'postgres'
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        return conn
    except Exception as e:
        st.error(f"Error al conectar a la base de datos: {e}")
        return None


# Función para mostrar la barra de carga
def show_loading_bar():
    with st.spinner('Tus datos se están registrando...'):
        progress_bar = st.progress(0)
        for percent_complete in range(100):
            time.sleep(0.05)
            progress_bar.progress(percent_complete + 1)

# Función para registrar un nuevo empleado
def registrar_empleado(id_empleado, nombre, apellido, sector_geriatrico, horario_entrada, horario_salida):
    try:
        conn = get_db_connection()
        if not conn:
            return False
        cur = conn.cursor()
        query = """
            INSERT INTO meditrack.empleado (ID_Empleado, nombre, apellido, sector_geriatrico, horario_entrada, horario_salida)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cur.execute(query, (id_empleado, nombre, apellido, sector_geriatrico, horario_entrada, horario_salida))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error al registrar empleado: {e}")
        return False

# Función para registrar un nuevo doctor
def registrar_doctor(id_doctor, nombre, apellido, hospital):
    try:
        conn = get_db_connection()
        if not conn:
            return False
        cur = conn.cursor()
        query = """
            INSERT INTO meditrack.doctores (ID_Doctor, nombre, apellido, hospital)
            VALUES (%s, %s, %s, %s)
        """
        cur.execute(query, (id_doctor, nombre, apellido, hospital))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error al registrar doctor: {e}")
        return False



# Función principal para la página de registro de usuarios
def main():
    st.title("Registrar usuario")

    nombre_input = st.text_input("Ingrese su Nombre:")
    apellido_input = st.text_input("Ingrese su Apellido:")
    ocupacion_input = st.selectbox("Seleccione su Ocupación:", ["Empleado", "Doctor"])

    if ocupacion_input == "Empleado":
        id_empleado_input = st.text_input("ID del Empleado:", placeholder= "Ej: 45072248")
        sector_geriatrico_input = st.text_input("Sector Geriátrico:")
        horario_entrada_input = st.time_input("Horario de Entrada:")
        horario_salida_input = st.time_input("Horario de Salida:")

        if st.button("Registrarse como Empleado"):
            show_loading_bar()
            if registrar_empleado(id_empleado_input, nombre_input, apellido_input, sector_geriatrico_input, horario_entrada_input, horario_salida_input):
                st.success("Empleado registrado exitosamente. Ahora puede iniciar sesión")
                st.page_link("pages/1_Iniciar_Sesión.py", label="Inicio", icon="➡️", help=None, disabled=False, use_container_width=None)

            else:
                st.error("Error al registrar empleado")

    elif ocupacion_input == "Doctor":
        id_doctor_input = st.text_input("ID del Doctor:", placeholder= "Ej: 45072248")
        hospital_input = st.text_input("Hospital:")

        if st.button("Registrarse como Doctor"):
            show_loading_bar()
            if registrar_doctor(id_doctor_input, nombre_input, apellido_input, hospital_input):
                st.success("Doctor registrado exitosamente. Ahora puede iniciar sesión")
                st.page_link("pages/1_Iniciar_Sesión.py", label="Inicio", icon="➡️", help=None, disabled=False, use_container_width=None)
            else:
                st.error("Error al registrar doctor")

if __name__ == "__main__":
    main()
