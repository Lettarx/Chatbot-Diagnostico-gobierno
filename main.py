import streamlit as st
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.messages import HumanMessage

from dotenv import load_dotenv
import os
from polpaico import Questions
from preeguntas import preguntas


env = load_dotenv(".env")
#Titulo de la aplicación
st.title("Diagnostico Nivel de Maduración GB")

#plantilla prompt
prompt_questions_only = ChatPromptTemplate(Questions)

#Ingresar Api desde .env
openai_api_key = os.environ.get("OPENAI_API_KEY")

#Cargar modelo de chat
model = init_chat_model("gpt-4o-mini", model_provider="openai")

#define un nuevo graph
workflow = StateGraph(state_schema=MessagesState)

#Definir la función que llama al modelo
def call_model(state: MessagesState):
  prompt = prompt_questions_only.invoke(state)
  response = model.invoke(state["messages"])
  return {"messages": response}

#Definir el nodo en el graph
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

#Añadir a la memoria
if "memory" not in st.session_state:
    st.session_state.memory = MemorySaver()
app = workflow.compile(checkpointer=st.session_state.memory)

#Maneja las sesiones
config = {"configurable": {"thread_id": "abc123"}}

#Fuuncion para autentificarse con openai
def generate_response(input_text):
    input_messages = [HumanMessage(input_text)]
    response = app.invoke(
        {"messages": input_messages},
        config
    )
    st.info(response["messages"][-1].content)

#Formulario del chatbot
with st.form("my_form"):
    #entrada   
    text = st.text_area(
        "Enter text:",
        "What are the three key pieces of advice for learning how to code?",
    )
    #Cuando se envia se realiza la solicitud
    submitted = st.form_submit_button("Submit")
    if not openai_api_key.startswith("sk-"):
        st.warning("Please enter your OpenAI API key!", icon="⚠")
    if submitted and openai_api_key.startswith("sk-"):
        generate_response(text)