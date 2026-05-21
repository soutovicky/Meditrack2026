import streamlit as st

# Configuración de la página con favicon
favicon = "https://github.com/soutovicky/Meditrack2/blob/main/Imagenes/Icon.png?raw=true"
st.set_page_config(page_title='Meditrack', page_icon=favicon, layout='wide')

# ✅ Este archivo no necesita conexión a la base de datos
# (solo maneja el estado de sesión local)

def logout():
    st.session_state['estado'] = 'No Autorizado'
    st.session_state['user_role'] = None
    st.session_state['user_id'] = None
    st.session_state['session_closed'] = True
    st.rerun()  # ✅ reemplaza experimental_rerun()

def logout_page():
    st.title("Cerrar Sesión")

    if st.session_state.get('session_closed', False):
        st.success("Sesión cerrada exitosamente.")
    elif st.session_state.get('estado') == 'Autorizado':
        st.write("Gracias por usar MediTrack. ¡Hasta pronto!")
        if st.button("Cerrar Sesión"):
            logout()
    else:
        st.error("Debe iniciar sesión primero para acceder a esta página.")

if 'estado' not in st.session_state:
    st.session_state['estado'] = 'No Autorizado'

logout_page()