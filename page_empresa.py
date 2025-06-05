import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from preeguntas import preguntas  
from prompts import prompt_preguntas, prompt_informe
import json
import os
from datetime import datetime
from pymongo import MongoClient


load_dotenv()

def guardar_resultado(empresa, respuestas, informe):
    try:
        id_documento = guardar_resultado_mongo(
            empresa=empresa,
            respuestas=respuestas,
            informe=informe,
        )
        st.success(f"✅ Archivo guardado exitosamente en: {id_documento}")
        return True

    except Exception as e:
        st.error(f"❌ Error al guardar el archivo: {str(e)}")
        return False
    


def guardar_resultado_mongo(empresa, respuestas, informe):
    # Puedes pasar el URI como variable de entorno para no dejarlo hardcodeado
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise Exception("No hay MONGO_URI configurado")

    client = MongoClient(mongo_uri)
    db = client["diagnosticos"]   # Nombre de la base de datos
    coleccion = db["resultados"]  # Nombre de la colección
    

    data = {
        "empresa": empresa,
        "fecha": datetime.now().isoformat(),
        "respuestas": [{"pregunta": q, "respuesta": r} for q, r in respuestas],
        "informe": informe
    }

    resultado = coleccion.insert_one(data)
    return resultado.inserted_id  # ID del documento insertado


def log_empresas():
    if not st.session_state.logged_in or st.session_state.user_type != "empresa":
        st.error("Acceso no autorizado")
        return
    
    load_dotenv()

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

        # Evitar duplicar informe si ya está generado
        if "informe_generado" not in st.session_state:

            model = ChatOpenAI(temperature=0)
            prompt_template_informe = ChatPromptTemplate.from_template(prompt_informe)

            resumen_respuestas = "\n".join(
                [f"{i+1}. {q}\nRespuesta: {r}" for i, (q, r) in enumerate(st.session_state.historial)]
            )

            prompt_informe_llm = prompt_template_informe.invoke({
                "resumen_respuestas": resumen_respuestas
            })

            informe = model.invoke(prompt_informe_llm).content

            # Guardar los datos
            if guardar_resultado(
                empresa=st.session_state.get("empresa_nombre", "empresa_default"),  
                respuestas=st.session_state.historial,
                informe=informe
            ):
                st.session_state.informe_generado = informe
            else:
                st.warning("No se pudo guardar el informe. Por favor, contacte al administrador.")

        # Mostrar el informe
        st.subheader("📋 Informe Final")
        st.markdown(st.session_state.informe_generado)
