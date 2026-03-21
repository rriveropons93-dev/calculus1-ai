import streamlit as st
from utils.firebase_utils import init_firebase
from utils.gemini_utils import init_gemini
from guest import modo_guest
from professor.professor import modo_profesor
from student.student import modo_student

db = init_firebase()
client = init_gemini()

if "modo" not in st.session_state:
    st.session_state.modo = None

if st.session_state.modo is None:
    st.title("📚 Calculus 1 AI Assistant")
    st.markdown("<small>Developed by Roger Riveropons | rriveropons93@gmail.com</small>", unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("Select your mode:")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("👤 Guest", use_container_width=True):
            st.session_state.modo = "guest"
            st.rerun()
    with col2:
        if st.button("🎓 Student", use_container_width=True):
            st.session_state.modo = "student"
            st.rerun()
    with col3:
        if st.button("👨‍🏫 Professor", use_container_width=True):
            st.session_state.modo = "professor"
            st.rerun()

elif st.session_state.modo == "guest":
    modo_guest(client)

elif st.session_state.modo == "student":
    modo_student(client,db)

elif st.session_state.modo == "professor":
    modo_profesor(db,client)
