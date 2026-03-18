import streamlit as st
from google import genai
import pdfplumber
import os

if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)

def cargar_pdfs(carpeta="pdfs"):
    texto_total = ""
    archivos = [f for f in os.listdir(carpeta) if f.endswith(".pdf")]
    for archivo in archivos:
        try:
            with pdfplumber.open(os.path.join(carpeta, archivo)) as pdf:
                for pagina in pdf.pages:
                    texto = pagina.extract_text()
                    if texto:
                        texto_total += texto + "\n"
        except Exception as e:
            st.warning(f"Reading Error {archivo}: {e}")
    return texto_total

st.title("📚 Calculus 1 AI Assistant")
st.caption("Ask questions about the course material.")

material = cargar_pdfs()

if not material:
    st.error("No material found in the pdfs folder.")    
    st.stop()

st.success(f"Material loaded: {len(material)} characters")

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if pregunta := st.chat_input("What do you want to study?"):
    st.session_state.mensajes.append({"role": "user", "content": pregunta})
    with st.chat_message("user"):
        st.write(pregunta)

    prompt = f"""Eres un asistente de Cálculo 1 para estudiantes. 

REGLAS:
- Para saludos y preguntas generales sobre qué puedes hacer, responde normalmente y amablemente.
- Para preguntas de Cálculo 1, usa SOLO el material del curso proporcionado. Puedes mejorar la didactica del curso, puedes entender las necesidaddes del estudiante, y usando el contenido como base principal ayudarlo a estudiar calculo.
- Si te preguntan algo de Cálculo que NO está en el material, di: 'Eso no está cubierto en el material del curso.'
- Responde siempre en el mismo idioma que usa el estudiante.
- Always respond in English unless the student writes in Spanish.

{material[:46986]}

PREGUNTA: {pregunta}"""

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            st.write(response.text)

    st.session_state.mensajes.append({"role": "assistant", "content": response.text})
