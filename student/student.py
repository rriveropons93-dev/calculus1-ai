import streamlit as st
import streamlit.components.v1 as components
from utils.pdf_utils import cargar_pdfs
from utils.prompt import get_prompt
from datetime import datetime

def modo_student(client, db):

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container {
        max-width: 780px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 1rem !important;
    }
    .student-title { font-size: 1rem; font-weight: 600; color: #1a1a2e; }
    .student-sub   { font-size: 0.72rem; color: #9ca3af; margin-bottom: 1rem; }
    </style>
    """, unsafe_allow_html=True)

    student_id = st.session_state.student_id
    material   = cargar_pdfs()

    # ── Header ────────────────────────────────────────────────────────────────
    col_title, col_back = st.columns([6, 1])
    with col_title:
        st.markdown("<div class='student-title'>📚 Calculus 1 AI</div>", unsafe_allow_html=True)
        info   = db.collection("usuarios").document(student_id).get().to_dict()
        nombre = info.get("first_name", student_id) if info else student_id
        st.markdown(f"<div class='student-sub'>Welcome, {nombre}</div>", unsafe_allow_html=True)
    with col_back:
        if st.button("logout", key="back_student"):
            st.session_state.modo = None
            st.session_state.student_id = None
            st.session_state.mensajes = []
            st.rerun()

    # ── Load chat history ─────────────────────────────────────────────────────
    if "mensajes" not in st.session_state:
        doc = db.collection("chats").document(student_id).get()
        st.session_state.mensajes = doc.to_dict().get("mensajes", []) if doc.exists else []
    
    anchor = st.empty()

    for msg in st.session_state.mensajes:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    anchor.markdown('<div id="bottom"></div>', unsafe_allow_html=True)

    # ── Chat input ────────────────────────────────────────────────────────────
    if pregunta := st.chat_input("What do you want to study?"):
        st.session_state.mensajes.append({"role": "user", "content": pregunta})
        with st.chat_message("user"):
            st.write(pregunta)

        prompt = get_prompt(material, pregunta)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                st.write(response.text)

        st.session_state.mensajes.append({"role": "assistant", "content": response.text})

        db.collection("chats").document(student_id).set({
            "mensajes": st.session_state.mensajes,
            "ultima_actualizacion": datetime.now().isoformat()
        })

        st.rerun()