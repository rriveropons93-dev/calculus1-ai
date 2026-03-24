import streamlit as st
from utils.firebase_utils import init_firebase
from utils.gemini_utils import init_gemini
from guest import modo_guest
from professor.professor import modo_profesor
from student.student import modo_student

st.set_page_config(page_title="Calculus 1 AI", page_icon="🎓", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.block-container {padding-top: 2rem; max-width: 500px;}
</style>
""", unsafe_allow_html=True)

db = init_firebase()
client = init_gemini()

if "modo" not in st.session_state:
    st.session_state.modo = None
if "student_id" not in st.session_state:
    st.session_state.student_id = None

if st.session_state.modo is None:
    st.markdown("<h4 style='text-align:center;margin-bottom:2px'>🎓 Calculus 1 AI Assistant</h4>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#888;font-size:12px;margin-bottom:16px'>Developed by Roger Riveropons</p>", unsafe_allow_html=True)

    with st.expander("ℹ️ Help & Features"):
        st.markdown("**👤 Guest** - Try the AI without logging in.")
        st.markdown("**🎓 Student** - Log in and chat. History saved.")
        st.markdown("**👨‍🏫 Professor** - View chats, analysis, weekly report.")

    _, col, _ = st.columns([1, 2, 1])
    with col:
        usuario = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login = st.button("Login", use_container_width=True)
        guest = st.button("Continue as Guest", use_container_width=True)
        register = st.button("📝 Register", use_container_width=True)

    if login:
        if not usuario or not password:
            st.error("Enter username and password.")
        else:
            doc = db.collection("usuarios").document(usuario).get()
            if doc.exists and doc.to_dict().get("password") == password:
                rol = doc.to_dict().get("rol")
                st.session_state.student_id = usuario
                st.session_state.modo = "professor" if rol == "professor" else "student"
                st.rerun()
            else:
                st.error("Invalid username or password.")

    if guest:
        st.session_state.modo = "guest"
        st.rerun()

    if register:
        st.session_state.modo = "register"
        st.rerun()

elif st.session_state.modo == "register":
    st.markdown("<h4 style='text-align:center'>📝 Create Account</h4>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 2, 1])
    with col:
        nuevo_usuario = st.text_input("Username")
        nuevo_password = st.text_input("Password", type="password")
        crear = st.button("Create Account", use_container_width=True)
        back = st.button("← Back", use_container_width=True)

    if crear:
        if not nuevo_usuario or not nuevo_password:
            st.error("Fill in all fields.")
        else:
            doc = db.collection("usuarios").document(nuevo_usuario).get()
            if doc.exists:
                st.error("Username already taken.")
            else:
                db.collection("usuarios").document(nuevo_usuario).set({
                    "id": nuevo_usuario,
                    "password": nuevo_password,
                    "rol": "student"
                })
                st.success("Account created! You can now log in.")
                st.session_state.modo = None
                st.rerun()

    if back:
        st.session_state.modo = None
        st.rerun()

elif st.session_state.modo == "guest":
    modo_guest(client)

elif st.session_state.modo == "student":
    modo_student(client, db)

elif st.session_state.modo == "professor":
    modo_profesor(client, db)