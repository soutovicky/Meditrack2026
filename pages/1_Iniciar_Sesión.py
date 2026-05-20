import streamlit as st
import psycopg2
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

# Función para verificar si el ID existe en la tabla 'empleado'
def check_id_in_empleado(id_to_check):
    try:
        conn = get_db_connection()
        if not conn:
            return None
        cur = conn.cursor()
        query = """
            SELECT ID_Empleado, nombre, apellido 
            FROM meditrack.empleado WHERE ID_Empleado = %s
        """
        cur.execute(query, (id_to_check,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result
    except Exception as e:
        st.error(f"Error al ejecutar la consulta en empleado: {e}")
        return None

# Función para verificar si el ID existe en la tabla 'doctores'
def check_id_in_doctores(id_to_check):
    try:
        conn = get_db_connection()
        if not conn:
            return None
        cur = conn.cursor()
        query = """
            SELECT ID_Doctor, nombre, apellido 
            FROM meditrack.doctores WHERE ID_Doctor = %s
        """
        cur.execute(query, (id_to_check,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result
    except Exception as e:
        st.error(f"Error al ejecutar la consulta en doctores: {e}")
        return None

# Función para actualizar detalles del usuario
def update_user_details(id, nombre, apellido,  table):
    try:
        conn = get_db_connection()
        if not conn:
            return
        cur = conn.cursor()
        if table == 'empleado':
            query = """
                UPDATE meditrack.empleado
                SET nombre = %s, apellido = %s
                WHERE ID_Empleado = %s
            """
        else:
            query = """
                UPDATE meditrack.doctores
                SET nombre = %s, apellido = %s 
                WHERE ID_Doctor = %s
            """
        cur.execute(query, (nombre, apellido,  id))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        st.error(f"Error al actualizar los detalles: {e}")

# Interfaz de Streamlit
st.title("Iniciar Sesión")

id_input = st.text_input("ID de Empleado o Doctor:", type="password", key="perfil_paciente_id")
#id_input = st.text_input("Ingrese el ID de Empleado o Doctor:")
nombre_input = st.text_input("Ingrese su Nombre:")
apellido_input = st.text_input("Ingrese su Apellido:")


if 'estado' not in st.session_state:
    st.session_state['estado']= 'No Autorizado'
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None

if st.button("Iniciar Sesion"):
    show_loading_bar()
    if not id_input or not nombre_input or not apellido_input:
        st.error("Por favor, complete todos los campos.")
    else:
        # Verificar en ambas tablas
        empleado_details = check_id_in_empleado(id_input)
        doctor_details = check_id_in_doctores(id_input)
        
        if empleado_details:
            update_user_details(id_input, nombre_input, apellido_input, 'empleado')
            st.session_state['user_id'] = id_input
            st.success("Inicio de sesión exitoso")
            st.write("¡Ahora puede ver novedades del Geriátrico en la página de Bienvenidos!")
            st.session_state['estado'] = 'Autorizado'
            st.session_state['user_role'] = 'Empleado'
            st.page_link("pages/3_Mi_Perfil.py", label="Mi Perfil", icon="➡️", help=None, disabled=False, use_container_width=None)
            st.page_link("Bienvenidos.py", label="Volver al Inicio", icon="➡️", help=None, disabled=False, use_container_width=None)

        elif doctor_details:
            update_user_details(id_input, nombre_input, apellido_input,  'doctor')
            st.session_state['user_id'] = id_input
            st.success("Inicio de sesión exitoso")
            st.write("¡Ahora puede ver novedades del Geriátrico en la página de Bienvenidos!")
            st.session_state['estado'] = 'Autorizado'
            st.session_state['user_role'] = 'Doctor'
            st.page_link("pages/3_Mi_Perfil.py", label="Mi Perfil", icon="➡️", help=None, disabled=False, use_container_width=None)
            st.page_link("Bienvenidos.py", label="Volver al Inicio", icon="➡️", help=None, disabled=False, use_container_width=None)

        else:
            st.error("El ID no existe en la base de datos.")