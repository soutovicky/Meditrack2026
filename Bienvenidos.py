import streamlit as st
from PIL import Image
import pandas as pd
import psycopg2
import os

# 'C:/Users/vicky.DESKTOP-TV6SV47/Downloads/pixelcut-export.png'

# Configuración de la página con favicon
favicon = "https://github.com/soutovicky/Meditrack2/blob/main/Imagenes/Icon.png?raw=true"
st.set_page_config(page_title='Meditrack', page_icon=favicon,layout='wide')


# CSS personalizado para los botones
def add_custom_css():
    st.markdown("""
        <style>
        .stButton button {
            border-radius: 8px;
            border: 2px solid #bf8cd4;
            padding: 10px 24px;
            background-color: #bf8cd4;
            color: white;
            font-size: 16px;
            margin: 10px 0;
        }
        </style>
    """, unsafe_allow_html=True)


# Configuración de la conexión a la base de datos
def get_db_connection():
    try:
        user = 'postgres.cetfptmtxzwdmidpxtuv'
        password = 'Meditrack2026'
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

col1, col2 = st.columns(2, gap="large")

def main():
    add_custom_css()
    st.title("¡Bienvenido a MediTrack!")

    # Dividir la pantalla en tres columnas
    col1, col2 = st.columns(2,gap="large")

    # Columna 1: Sección para usuarios existentes
    with col1:
        st.header("¿Ya tenés una cuenta?")
        if st.button("Iniciar Sesión"):
            st.switch_page("pages/1_Iniciar_Sesión.py")
            #st.page_link("pages/1_Iniciar_Sesión.py", label="Inicio", icon="➡", help=None, disabled=False, use_container_width=None)
            

    # Columna 2: Sección para nuevos usuarios
    with col2:
        st.header("¿Sos nuevo en la aplicación?")
        if st.button("Registrarse"):
            st.switch_page("pages/2_Registrarse.py")
            #st.page_link("pages/2_Registrarse.py", label="Registrarse", icon="➡", help=None, disabled=False, use_container_width=None)
            

# Función para obtener los empleados por sector geriátrico
def get_empleados_por_sector():
    try:
        conn = get_db_connection()
        if not conn:
            return None
        cur = conn.cursor()
        query = """
            SELECT sector_geriatrico, nombre, apellido
            FROM meditrack.empleado
            ORDER BY sector_geriatrico
        """
        cur.execute(query)
        result = cur.fetchall()
        cur.close()
        conn.close()
        return result
    except Exception as e:
        st.error(f"Error al obtener empleados por sector geriátrico: {e}")
        return None

# Función para mostrar el logo de la página
def show_logo():
    #logo_path = os.path.join(os.path.dirname('C:/Users/vicky.DESKTOP-TV6SV47/Documents/GitHub/Meditrack2/Imagenes/Logo.png'), 'Imagenes', 'Logo.png')
    #logo = Image.open('C:/Users/vicky.DESKTOP-TV6SV47/Documents/GitHub/Meditrack2/Imagenes/Logo.png')  # Reemplaza con la ruta a tu imagen de logo
    #logo = Image.open(logo_path)
    #st.image(logo, width=500)
    logo_url = "https://github.com/soutovicky/Meditrack2/blob/main/Imagenes/Logo.png?raw=true"
    st.image(logo_url, use_column_width=True, width=500)

# Función para mostrar el menú principal
def show_main_menu():
    st.sidebar.title("Menú Principal")
    menu_options = ["Noticias", "Planning"]
    choice = st.sidebar.selectbox("Seleccione una opción:", menu_options)

    if choice == "Noticias":
        show_forum_news()
    elif choice == "Planning":
        planning_page()
    
# Funciones de página (agrega tus funciones existentes aquí)
def show_forum_news():
    st.subheader("Noticias del Foro")
    forum_news = [
        {"title": "Inauguración de una nueva área de recreación:", "content": "El geriátrico ha inaugurado una nueva área de recreación para sus residentes. Esta área cuenta con jardines, bancos, juegos de mesa y un espacio para actividades al aire libre, brindando así un entorno agradable y estimulante para el bienestar de los residentes.", "foto": "https://github.com/soutovicky/Meditrack2/blob/main/Imagenes/arearecreacion.jpeg?raw=true"},
        {"title": "Celebración del Día del Abuelo:", "content": """
*¡Celebremos juntos el Día del Abuelo en el Geriátrico "Amor y Cuidado"!*

Estimados residentes y familias,

Nos complace invitarlos cordialmente a nuestra celebración especial del Día del Abuelo, que se llevará a cabo el próximo viernes 25 de agosto, en el salón principal del geriátrico.

*Fecha:* Viernes, 25 de agosto de 2024  
*Horario:* 16:00 - 18:00 horas  
*Lugar:* Salón principal del Geriátrico "Amor y Cuidado"

Durante esta festiva jornada, tendrán la oportunidad de disfrutar de una tarde llena de alegría y compañía. Entre las actividades programadas para el evento, destacamos:

- *Recepción y bienvenida:* Les recibiremos con música y una cálida bienvenida a cargo de nuestro equipo de cuidadores.
  
- *Actuación musical en vivo:* Disfrutaremos de la dulzura de la música en vivo, con un repertorio de canciones clásicas que evocarán hermosos recuerdos.

- *Show de magia y entretenimiento:* Un mago profesional nos sorprenderá con un espectáculo lleno de ilusiones y diversión para todas las edades.

- *Merienda especial:* Compartiremos una exquisita merienda con una selección de tortas, tartas, bocadillos y bebidas refrescantes.

- *Entrega de obsequios:* Cada abuelo y abuela recibirá un pequeño obsequio como muestra de nuestro aprecio y cariño.

Agradecemos de antemano su participación y les animamos a sumarse a esta celebración tan especial. Será un momento único para compartir sonrisas, afecto y gratos momentos en compañía de sus seres queridos y amigos del geriátrico.

¡Los esperamos con los brazos abiertos para celebrar juntos el amor y la sabiduría de nuestros queridos abuelos!

Atentamente,  
El equipo de "Amor y Cuidado"
""", "foto": "https://github.com/soutovicky/Meditrack2/blob/main/Imagenes/Pagina-Dia-de-los-Abuelos.jpg?raw=true"},
        {"title": "Charla sobre prevención de caídas:", "content": "El geriátrico ofreció una charla informativa sobre la prevención de caídas en personas mayores. La charla fue dictada por un especialista en geriatría y abordó temas como el fortalecimiento muscular, la importancia de mantener un hogar seguro y consejos para evitar accidentes. Los residentes y sus familias recibieron útiles recomendaciones para promover la seguridad y la autonomía en la vida diaria.", "foto": "https://github.com/soutovicky/Meditrack2/blob/main/Imagenes/prevencion.png?raw=true"}
    ]
    for news in forum_news:
        st.write(f"{news['title']}")
        st.write(news['content'])
        if 'foto' in news:
            st.image(news['foto'], width=300)
        st.write("---")
        

def logout():
    st.session_state['estado'] = 'No Autorizado'
    st.session_state['user_role'] = None
    st.session_state['user_id'] = None
    st.experimental_rerun()

def planning_page():
    st.title("Planning")

    # Obtener los datos de los empleados por sector geriátrico
    empleados = get_empleados_por_sector()

    if empleados:
        # Convertir los datos a un DataFrame de pandas
        df = pd.DataFrame(empleados, columns=['Sector Geriátrico', 'Nombre', 'Apellido'])

        # Mostrar los datos en forma de tabla
        st.dataframe(df)

    else:
        st.warning("No se encontraron empleados en la base de datos.")


# Página de bienvenida
def welcome_page():
    show_logo()
    st.write("""

Meditrack es una aplicación diseñada para facilitar la gestión de información médica en entornos hospitalarios. Con Meditrack, los profesionales de la salud pueden gestionar pacientes, prescripciones médicas y horarios de administración de medicamentos de manera eficiente y segura.

## Funcionalidades Principales:

1. *Gestión de Pacientes:* Registre y acceda fácilmente a la información de los pacientes, incluidos detalles personales, diagnósticos, alergias, contactos de emergencia y más.

2. *Prescripciones Médicas:* Cree y administre prescripciones médicas de forma intuitiva, especificando medicamentos, dosis, horarios de administración y asignación a pacientes y médicos.

3. *Asignación de Pacientes a Médicos:* Asigne pacientes a médicos para un seguimiento y cuidado personalizado, lo que facilita una comunicación efectiva y una atención centrada en el paciente.

4. *Administración de Medicamentos:* Controle la administración de medicamentos de manera precisa, registrando cuándo se administra cada dosis y manteniendo un historial completo de administración.

5. *Horarios de Trabajo:* Visualice los horarios de trabajo de los empleados del hospital, lo que ayuda a coordinar eficientemente las tareas y garantizar una cobertura adecuada en todas las áreas.

## Beneficios de Meditrack:

- *Eficiencia:* Simplifica y automatiza tareas administrativas, lo que permite a los profesionales de la salud centrarse en la atención al paciente.
- *Seguridad:* Almacena datos médicos de forma segura y cumple con los estándares de privacidad y seguridad de la información.
- *Personalización:* Adaptable a las necesidades específicas de cada hospital o clínica, proporcionando una solución flexible y escalable.
- *Accesibilidad:* Permite el acceso a la información médica desde cualquier dispositivo con conexión a internet, facilitando la colaboración entre equipos médicos.

## Únete a la Revolución en Gestión Médica con Meditrack.
""")

# Lógica principal de la aplicación
if 'estado' not in st.session_state:
    st.session_state['estado'] = 'No Autorizado'

if st.session_state['estado'] == 'Autorizado':
    show_main_menu()
else:
    main()
    welcome_page()
    st.error("Debes iniciar sesión para acceder a tu Menu Principal.")

