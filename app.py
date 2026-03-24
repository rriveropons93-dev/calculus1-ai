import streamlit as st
from utils.firebase_utils import init_firebase
from utils.gemini_utils import init_gemini
from guest import modo_guest
from professor.professor import modo_profesor
from student.student import modo_student
 
# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Calculus 1 AI",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed",
)
 
# ── Global styles ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&display=swap');
 
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
 
#MainMenu, footer, header { visibility: hidden; }
 
.block-container {
    padding-top: 3rem;
    max-width: 420px;
}
 
/* ── Card ── */
.card {
    background: #ffffff;
    border: 1px solid #e8eaf0;
    border-radius: 16px;
    padding: 2rem 2rem 1.5rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.06);
}
 
/* ── Title block ── */
.app-title {
    text-align: center;
    font-size: 1.5rem;
    font-weight: 600;
    color: #1a1a2e;
    margin-bottom: 2px;
}
.app-subtitle {
    text-align: center;
    font-size: 0.78rem;
    color: #9ca3af;
    margin-bottom: 1.6rem;
    letter-spacing: 0.02em;
}
 
/* ── Divider ── */
.divider {
    border: none;
    border-top: 1px solid #f0f0f5;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)
 
# ── Init services ─────────────────────────────────────────────────────────────
db     = init_firebase()
client = init_gemini()
 
# ── Session defaults ──────────────────────────────────────────────────────────
st.session_state.setdefault("modo", None)
st.session_state.setdefault("student_id", None)
 
# ─────────────────────────────────────────────────────────────────────────────
#  LOGIN
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.modo is None:
 
    st.markdown("<div class='app-title'>🎓 Calculus 1 AI Assistant</div>", unsafe_allow_html=True)
    st.markdown("<div class='app-subtitle'>Developed by Roger Rivero</div>", unsafe_allow_html=True)
 
    with st.expander("ℹ️ Help & Features"):
        st.markdown(
            "**👤 Guest** — Try the AI without logging in.  \n"
            "**🎓 Student** — Log in and chat. History saved.  \n"            
        )
 
    usuario  = st.text_input("Username")
    password = st.text_input("Password", type="password")
 
    col1, col2 = st.columns(2)
    login    = col1.button("Login",            use_container_width=True, type="primary")
    guest    = col2.button("Continue as Guest", use_container_width=True)
    register = st.button("📝 Register", use_container_width=True)
 
    if login:
        if not usuario or not password:
            st.error("Please enter your username and password.")
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
 
# ─────────────────────────────────────────────────────────────────────────────
#  REGISTER
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.modo == "register":
 
    st.markdown("<div class='app-title'>📝 Create Account</div>", unsafe_allow_html=True)
    st.markdown("<div class='app-subtitle'>Join as a student</div>", unsafe_allow_html=True)
 
    nuevo_usuario  = st.text_input("Username")
    nuevo_password = st.text_input("Password", type="password")
 
    col1, col2 = st.columns(2)
    crear = col1.button("Create Account", use_container_width=True, type="primary")
    back  = col2.button("← Back",         use_container_width=True)
 
    if crear:
        if not nuevo_usuario or not nuevo_password:
            st.error("Please fill in all fields.")
        elif db.collection("usuarios").document(nuevo_usuario).get().exists:
            st.error("Username already taken.")
        else:
            db.collection("usuarios").document(nuevo_usuario).set({
                "id":       nuevo_usuario,
                "password": nuevo_password,
                "rol":      "student",
            })
            st.success("Account created! You can now log in.")
            st.session_state.modo = None
            st.rerun()
 
    if back:
        st.session_state.modo = None
        st.rerun()
 
# ─────────────────────────────────────────────────────────────────────────────
#  APP MODES
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.modo == "guest":
    modo_guest(client)
 
elif st.session_state.modo == "student":
    modo_student(client, db)
 
elif st.session_state.modo == "professor":
    modo_profesor(client, db)