import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from supabase_client import db

load_dotenv()

favicon = "https://github.com/soutovicky/Meditrack2026/blob/main/Imagenes/Icon.png?raw=true"
st.set_page_config(page_title='Meditrack', page_icon=favicon, layout='wide')


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


def main():
    add_custom_css()
    st.title("¡Bienvenido a MediTrack!")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.header("¿Ya tenés una cuenta?")
        if st.button("Iniciar Sesión"):
            st.switch_page("pages/1_Iniciar_Sesión.py")

    with col2:
        st.header("¿Sos nuevo en la aplicación?")
        if st.button("Registrarse"):
            st.switch_page("pages/2_Registrarse.py")


def get_empleados_por_sector():
    try:
        response = db().table("empleado") \
            .select("sector_hospitalario, nombre, apellido, cargo") \
            .order("sector_hospitalario") \
            .execute()
        return response.data if response.data else None
    except Exception as e:
        st.error(f"Error al obtener empleados: {e}")
        return None


def show_logo():
    logo_url = "https://github.com/soutovicky/Meditrack2/blob/main/Imagenes/Logo.png?raw=true"
    st.image(logo_url, width=500)


def show_main_menu():
    st.sidebar.title("Menú Principal")
    menu_options = ["Noticias", "Planning"]
    choice = st.sidebar.selectbox("Seleccione una opción:", menu_options)

    if choice == "Noticias":
        show_forum_news()
    elif choice == "Planning":
        planning_page()


def show_forum_news():
    st.subheader("Noticias de la Institución")
    forum_news = [
        {
            "title": "Inauguración de nueva sala de espera:",
            "content": "La institución ha inaugurado una nueva sala de espera para pacientes y familiares. El espacio cuenta con asientos cómodos, señalización clara y conexión Wi-Fi, brindando un ambiente más agradable durante la estadía.",
            "foto": "https://github.com/soutovicky/Meditrack2026/blob/main/Imagenes/arearecreacion.jpeg?raw=true"
        },
        {
            "title": "Jornada de capacitación en seguridad del paciente:",
            "content": """
*¡El equipo de MediTrack los invita a la jornada anual de seguridad farmacológica!*

Estimado personal de salud,

Nos complace convocarlos a nuestra capacitación anual orientada a reducir errores en la administración de medicamentos y mejorar la coordinación entre médicos, enfermeros y farmacia.

*Fecha:* Viernes 25 de agosto de 2024
*Horario:* 14:00 - 18:00 horas
*Lugar:* Auditorio principal de la institución

Entre los temas a tratar:
- Uso correcto del sistema MediTrack
- Protocolos de verificación de identidad del paciente
- Manejo de alertas por alergias e interacciones farmacológicas
- Registro digital de administración de medicamentos
"""
        },
        {
            "title": "Recordatorio: protocolo de verificación de medicamentos:",
            "content": "Se recuerda a todo el personal que antes de administrar cualquier medicamento debe verificar los cinco correctos: paciente correcto, medicamento correcto, dosis correcta, vía correcta y horario correcto. MediTrack automatiza esta verificación, pero el control humano sigue siendo esencial.",
            "foto": "https://github.com/soutovicky/Meditrack2/blob/main/Imagenes/prevencion.png?raw=true"
        }
    ]
    for news in forum_news:
        st.write(f"**{news['title']}**")
        st.write(news['content'])
        if 'foto' in news:
            st.image(news['foto'], width=300)
        st.write("---")


def logout():
    st.session_state['estado'] = 'No Autorizado'
    st.session_state['user_role'] = None
    st.session_state['user_id'] = None
    st.rerun()


def planning_page():
    st.title("Planning del Personal")
    empleados = get_empleados_por_sector()
    if empleados:
        df = pd.DataFrame(empleados)
        df.columns = ['Sector', 'Nombre', 'Apellido', 'Cargo']
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No se encontraron empleados en la base de datos.")


def welcome_page():
    show_logo()
    st.write("""
MediTrack es un sistema inteligente de seguridad farmacológica hospitalaria. Conecta digitalmente a médicos, enfermeros y administración para reducir errores en la prescripción y administración de medicamentos.

## Funcionalidades Principales:

1. **Gestión de Pacientes:** Registre y acceda a información clínica actualizada, incluyendo diagnósticos, alergias y contactos de emergencia.

2. **Prescripciones Médicas:** Los médicos crean prescripciones digitales vinculadas al paciente, con validación automática de alergias e interacciones.

3. **Administración de Medicamentos:** Los enfermeros registran cada dosis administrada con fecha y hora, generando trazabilidad completa.

4. **Alertas Clínicas:** El sistema emite alertas automáticas ante situaciones críticas o cambios en el estado del paciente.

5. **Horarios y Planning:** Visualización del personal por sector para coordinar la cobertura de cada turno.

## Beneficios de MediTrack:

- **Seguridad:** Barrera digital que previene errores de medicación.
- **Trazabilidad:** Registro completo y auditable de cada administración.
- **Eficiencia:** Elimina la fragmentación de información entre médicos y enfermeros.
- **Accesibilidad:** Disponible desde cualquier dispositivo con conexión a internet.
""")


if 'estado' not in st.session_state:
    st.session_state['estado'] = 'No Autorizado'

if st.session_state['estado'] == 'Autorizado':
    show_main_menu()
else:
    main()
    welcome_page()
    st.error("Debes iniciar sesión para acceder al sistema.")