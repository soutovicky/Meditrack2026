import streamlit as st

favicon = "https://github.com/soutovicky/Meditrack2/blob/main/Imagenes/Icon.png?raw=true"
st.set_page_config(page_title='Meditrack', page_icon=favicon, layout='wide')


def logout():
    st.session_state['estado']         = 'No Autorizado'
    st.session_state['user_role']      = None
    st.session_state['user_id']        = None
    st.session_state['session_closed'] = True
    st.rerun()


def logout_page():
    st.title("Cerrar Sesión")

    # Si la sesión está autorizada, resetear session_closed para mostrar el botón
    if st.session_state.get('estado') == 'Autorizado':
        st.session_state['session_closed'] = False

    if st.session_state.get('session_closed', False):
        st.success("✅ Sesión cerrada exitosamente.")
        st.write("Puede cerrar esta ventana o volver al inicio.")
        st.page_link("Bienvenidos.py", label="Volver al Inicio", icon="🏠")

    elif st.session_state.get('estado') == 'Autorizado':
        st.write(f"Sesión activa como **{st.session_state.get('user_role')}** (ID: {st.session_state.get('user_id')})")
        st.write("¿Está seguro que desea cerrar sesión?")
        if st.button("Cerrar Sesión"):
            logout()

    else:
        st.error("No hay una sesión activa.")
        st.page_link("Bienvenidos.py", label="Iniciar Sesión", icon="🏠")


if 'estado' not in st.session_state:
    st.session_state['estado'] = 'No Autorizado'

logout_page()