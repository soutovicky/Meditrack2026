import streamlit as st
import psycopg2
from PIL import Image
from io import BytesIO

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

# Función para buscar el ID del paciente por nombre y apellido
def buscar_id_paciente(nombre, apellido):
    try:
        conn = get_db_connection()
        if not conn:
            return None
        cur = conn.cursor()
        query = """
            SELECT ID_Pacientes, nombre, apellido
            FROM meditrack.pacientes
            WHERE nombre = %s AND apellido = %s
        """
        cur.execute(query, (nombre, apellido))
        result = cur.fetchall()
        cur.close()
        conn.close()
        return result
    except Exception as e:
        st.error(f"Error al buscar el ID del paciente: {e}")
        return None
    

def buscar_id_paciente_page():
    #st.set_page_config(page_title="Buscar ID de Paciente", page_icon="🔍")
    st.title("Buscar ID de Paciente")

    # Agregar una imagen o icono
    #st.image("https://via.placeholder.com/150", caption="Encuentra el ID del paciente", use_column_width=True)

    nombre = st.text_input("Nombre del Paciente", key="nombre_paciente")
    apellido = st.text_input("Apellido del Paciente", key="apellido_paciente")

    if st.button("Buscar ID", key="btn_buscar_id"):
        if nombre and apellido:
            pacientes = buscar_id_paciente(nombre, apellido)
            if pacientes:
                if len(pacientes) == 1:
                    st.success(f"ID del Paciente: {pacientes[0][0]}")
                else:
                    st.warning("Se encontraron múltiples pacientes con el mismo nombre y apellido.")
                    for paciente in pacientes:
                        st.write(f"ID: {paciente[0]}, Nombre: {paciente[1]}, Apellido: {paciente[2]}")
            else:
                st.warning("No se encontró ningún paciente con ese nombre y apellido.")
        else:
            st.error("Por favor, complete ambos campos.")



# Inicializar el estado de la sesión
if 'estado' not in st.session_state:
    st.session_state['estado'] = 'No Autorizado'
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None

# Ejecutar la página de búsqueda
if st.session_state['estado'] == 'Autorizado':
    buscar_id_paciente_page()
else:
    st.title("Usted aún no puede buscar un Paciente")
    st.error("Debes iniciar sesión primero.")
