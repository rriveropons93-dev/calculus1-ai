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
if "student_id" not in st.session_state:
    st.session_state.student_id = None
if "rol" not in st.session_state:
    st.session_state.rol = None

if st.session_state.modo is None:
    st.title("🎓 Calculus 1 AI Assistant")
    st.markdown("<small>Developed by Roger Riveropons | rriveropons93@gmail.com</small>", unsafe_allow_html=True)
    st.markdown("---")

    if st.expander("ℹ️ Help & Features"):
        st.markdown("**👤 Guest** - Try the AI assistant without logging in. No history saved.")
        st.markdown("**🎓 Student** - Log in, chat with AI, history saved for professor.")
        st.markdown("**👨‍🏫 Professor** - View student chats, AI analysis, weekly report.")

    st.subheader("Login")
    with st.form("login_form"):
        usuario = st.text_input("Username")
        password = st.text_input("Password", type="password")
        col1, col2 = st.columns(2)
        with col1:
            login = st.form_submit_button("Login", use_container_width=True)
        with col2:
            guest = st.form_submit_button("Continue as Guest", use_container_width=True)

    if login:
        if usuario.strip() == "" or password.strip() == "":
            st.error("Please enter username and password.")
        else:
            doc = db.collection("usuarios").document(usuario).get()
            if doc.exists:
                data = doc.to_dict()
                if data.get("password") == password:
                    rol = data.get("rol")
                    st.session_state.student_id = usuario
                    st.session_state.rol = rol
                    if rol == "professor":
                        st.session_state.modo = "professor"
                    else:
                        st.session_state.modo = "student"
                    st.rerun()
                else:
                    st.error("Incorrect password.")
            else:
                st.error("User not found.")

    if guest:
        st.session_state.modo = "guest"
        st.rerun()

    st.markdown("---")
    if st.button("📝 Register", use_container_width=True):
        st.session_state.modo = "register"
        st.rerun()

elif st.session_state.modo == "register":
    st.title("📝 Create Account")
    with st.form("register_form"):
        nuevo_usuario = st.text_input("Username")
        nuevo_password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Create Account")

    if st.button("← Back"):
        st.session_state.modo = None
        st.rerun()

    if submitted:
        if nuevo_usuario.strip() == "" or nuevo_password.strip() == "":
            st.error("Please fill in all fields.")
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

elif st.session_state.modo == "guest":
    modo_guest(client)

elif st.session_state.modo == "student":
    modo_student(client, db)

elif st.session_state.modo == "professor":
    modo_profesor(client, db)
