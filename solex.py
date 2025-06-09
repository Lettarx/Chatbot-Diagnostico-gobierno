"""
Interfaz y logica para el dashboard de Solex
"""

import os
import streamlit as st
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

def mostrar_vista_solex():
    """
    Muestra la vista principal de Solex.
    """
    st.title("Bienvenido a Solex")
    st.write("Esta es la página de inicio de Solex. " \
    "Aquí puedes acceder a todas las funcionalidades del sistema.")
    # Recolectar reportes mongo
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client["diagnosticos"]
    coleccion = db["resultados"]

    # Obtener TODOS los datos de una vez
    informes_todo = list(coleccion.find({}))

    with st.form("formulario_informes"):
        st.write("### Informes de Empresas")
        st.write("Selecciona un informe para ver los detalles.")
        informe_seleccionado = st.selectbox(
            "Selecciona un informe de empresa", 
            informes_todo,
            format_func=lambda x: f"{x['empresa']} - {x['fecha']}"
        )
        sub = st.form_submit_button("Cargar Informe")

    if sub and informe_seleccionado:
        st.subheader(f"Informe de {informe_seleccionado['empresa']} - {
            informe_seleccionado['fecha']}")
        st.write("### Respuestas:")
        for respuesta in informe_seleccionado['respuestas']:
            with st.expander(f"📝 {respuesta['pregunta']}"):
                st.write(respuesta['respuesta'])
        st.write("### Informe Final:")
        st.write(informe_seleccionado['informe'])
