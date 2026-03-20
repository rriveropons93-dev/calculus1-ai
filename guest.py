import streamlit as st
from google import genai
from pdf_utils import cargar_pdfs
from prompt import get_prompt

def modo_guest(client):
    material = cargar_pdfs()
    if not material:
        st.error("No material found in the pdfs folder.")
        st.stop()

    st.title("📚 Calculus 1 AI Assistant")
    st.markdown("<small>Developed by Roger Riveropons | rriveropons93@gmail.com</small>", unsafe_allow_html=True)

    if st.button("← Back"):
        st.session_state.modo = None
        st.session_state.mensajes = []
        st.rerun()

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

        prompt = get_prompt(material, pregunta)

        st.markdown('<div id="top-response"></div>', unsafe_allow_html=True)
        st.markdown("<br><br>", unsafe_allow_html=True)

        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                st.write(response.text)

        st.session_state.mensajes.append({"role": "assistant", "content": response.text})

        st.components.v1.html("""
        <script>
            setTimeout(function() {
                window.parent.document.getElementById('top-response').scrollIntoView({behavior: 'smooth', block: 'start'});
            }, 1200);
        </script>
        """, height=0)
