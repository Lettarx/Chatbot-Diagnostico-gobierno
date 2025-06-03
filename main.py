import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

from preeguntas import preguntas  
from prompts import prompt_preguntas

# Configuración de la página
st.set_page_config(page_title="Entrevista Pre Diagnóstico")

# Inicializar estado de sesión
if "indice_pregunta" not in st.session_state:
    st.session_state.indice_pregunta = 0
if "historial" not in st.session_state:
    st.session_state.historial = []
if "comenzado" not in st.session_state:
    st.session_state.comenzado = True  # Lo activamos por defecto

# Configurar el modelo
model = ChatOpenAI(temperature=0)
prompt_template = ChatPromptTemplate.from_template(prompt_preguntas)

st.title("Entrevista de Diagnóstico en Gobierno de Datos")

# Mostrar historial anterior usando st.chat_message
for i, (pregunta, respuesta) in enumerate(st.session_state.historial):
    with st.chat_message("assistant"):
        st.markdown(f"**Pregunta {i+1}:** {pregunta}")
    with st.chat_message("user"):
        st.markdown(respuesta)

# Flujo de la entrevista
if st.session_state.indice_pregunta < len(preguntas):
    pregunta_actual = preguntas[st.session_state.indice_pregunta]

    # Mostrar pregunta en la interfaz tipo chat
    with st.chat_message("assistant"):
        st.markdown(f"{pregunta_actual}")

    # Entrada del usuario
    user_input = st.chat_input("💬 Tu respuesta:")

    if user_input:
        # Guardar historial
        st.session_state.historial.append((pregunta_actual, user_input))

        # Generar respuesta del modelo
        prompt = prompt_template.invoke({
            "pregunta_actual": pregunta_actual,
            "respuesta_usuario": user_input
        })
        respuesta_modelo = model.invoke(prompt)

        # Mostrar respuesta del modelo
        with st.chat_message("assistant"):
            st.markdown(respuesta_modelo.content)

        # Avanzar a la siguiente pregunta
        st.session_state.indice_pregunta += 1
        st.rerun()
else:
    st.success("✅ Entrevista completada. ¡Gracias!")
