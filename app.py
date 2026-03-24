import streamlit as st
from utils.firebase_utils import init_firebase
from utils.gemini_utils import init_gemini
from guest import modo_guest
from professor.professor import modo_profesor
from student.student import modo_student
 
st.set_page_config(
    page_title="Calculus 1 AI",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed",
)
 
modo_actual = st.session_state.get("modo")
max_w = "780px" if modo_actual in ("student", "guest") else "420px"
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&display=swap');
html, body, [class*="css"] {{ font-family: 'DM Sans', sans-serif; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding-top: 2rem; max-width: {max_w}; }}
.app-title {{ text-align:center; font-size:1.5rem; font-weight:600; color:#1a1a2e; margin-bottom:2px; }}
.app-subtitle {{ text-align:center; font-size:0.78rem; color:#9ca3af; margin-bottom:1.6rem; letter-spacing:.02em; }}
</style>
""", unsafe_allow_html=True)
 
db     = init_firebase()
client = init_gemini()
 
st.session_state.setdefault("modo", None)
st.session_state.setdefault("student_id", None)
 
PROFESSOR_USER = "Brennan"
PROFESSOR_PASS = "1234"
 
# ── Restore session from query params (e.g. after HTML link click) ────────────
params = st.query_params
if "modo" in params and st.session_state.modo is None:
    if params["modo"] == "professor":
        st.session_state.modo = "professor"
        st.session_state.student_id = PROFESSOR_USER
        if "open_student" in params:
            st.session_state.estudiante_seleccionado = params["open_student"]
            st.session_state.prof_vista = "detalle"
        else:
            st.session_state.setdefault("prof_vista", "lista")
        st.query_params.clear()
        st.rerun()
 
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.modo is None:
 
    st.markdown("<div class='app-title'>🎓 Calculus 1 AI Assistant</div>", unsafe_allow_html=True)
    st.markdown("<div class='app-subtitle'>Developed by Roger Riveropons</div>", unsafe_allow_html=True)
 
    with st.expander("ℹ️ Help & Features"):
        st.markdown(
            "**👤 Guest** — Try the AI without logging in.  \n"
            "**🎓 Student** — Log in and chat. History saved.  \n"
        )
 
    usuario  = st.text_input("Username")
    password = st.text_input("Password", type="password")
 
    col1, col2 = st.columns(2)
    login    = col1.button("Login",             use_container_width=True, type="primary")
    guest    = col2.button("Continue as Guest", use_container_width=True)
    register = st.button("📝 Register", use_container_width=True)
 
    if login:
        if not usuario or not password:
            st.error("Please enter your username and password.")
        elif usuario == PROFESSOR_USER and password == PROFESSOR_PASS:
            st.session_state.student_id = usuario
            st.session_state.modo = "professor"
            st.rerun()
        else:
            doc = db.collection("usuarios").document(usuario).get()
            if doc.exists and doc.to_dict().get("password") == password:
                st.session_state.student_id = usuario
                st.session_state.modo = "student"
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
 
    st.markdown("<div class='app-title'>📝 Create Account</div>", unsafe_allow_html=True)
    st.markdown("<div class='app-subtitle'>Join as a student</div>", unsafe_allow_html=True)
 
    first_name = st.text_input("First Name")
    last_name  = st.text_input("Last Name")
    student_id = st.text_input("Student ID")
 
    col1, col2 = st.columns(2)
    crear = col1.button("Create Account", use_container_width=True, type="primary")
    back  = col2.button("← Back",         use_container_width=True)
 
    if crear:
        if not first_name or not last_name or not student_id:
            st.error("Please fill in all fields.")
        elif student_id == PROFESSOR_USER:
            st.error("That username is reserved.")
        elif db.collection("usuarios").document(student_id).get().exists:
            st.error("Student ID already registered.")
        else:
            db.collection("usuarios").document(student_id).set({
                "id":         student_id,
                "first_name": first_name,
                "last_name":  last_name,
                "password":   student_id,
                "rol":        "student",
            })
            st.success(f"Account created for {first_name} {last_name}! You can now log in.")
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