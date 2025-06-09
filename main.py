"""
Pagina principal para iniciar sesión y redirigir a la vista
correspondiente según el tipo de usuario.
"""

import streamlit as st
from empresa import mostrar_vista_empresa
from solex import mostrar_vista_solex

st.set_page_config(
    page_title="Entrevista Pre Diagnóstico",
    page_icon=":clipboard:",
    layout='centered',
    initial_sidebar_state='collapsed'
)

# Inicialización de estados
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_type" not in st.session_state:
    st.session_state.user_type = None

def login():
    """
    Muestra el formulario de inicio de sesión.
    Permite a los usuarios iniciar sesión como Empresa o Solex."""
    with st.form("login_form"):
        st.title("Iniciar Sesión")
        st.write("Por favor, introduce tus credenciales para continuar.")
        usuario = st.text_input("Usuario:")
        contraseña = st.text_input("Contraseña:", type="password")
        submit_button = st.form_submit_button("Iniciar Sesión")
        if submit_button:
            if usuario == "empresa" and contraseña == "empresa123":
                st.success("¡Inicio de sesión exitoso como Empresa!")
                st.session_state.logged_in = True
                st.session_state.user_type = "empresa"
                st.rerun()
            elif usuario == "solex" and contraseña == "solex123":
                st.success("¡Inicio de sesión exitoso como Solex!")
                st.session_state.logged_in = True
                st.session_state.user_type = "solex"
                st.rerun()
            else:
                st.error("Credenciales incorrectas. Inténtalo de nuevo.")

if __name__ == "__main__":
    if not st.session_state.logged_in:
        login()
    else:
        # Mostrar la vista correspondiente según el tipo de usuario
        if st.session_state.user_type == "empresa":
            mostrar_vista_empresa()
        elif st.session_state.user_type == "solex":
            mostrar_vista_solex()
