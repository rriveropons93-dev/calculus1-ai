import streamlit as st
from datetime import datetime, timedelta
 
STYLES = """
<style>
.section-title {
    font-size: 0.7rem; font-weight: 600; letter-spacing: 0.08em;
    text-transform: uppercase; color: #9ca3af; margin-bottom: 0.6rem;
}
/* Make student buttons look like list rows */
div[data-testid="stVerticalBlock"] button[kind="secondary"] {
    background: transparent !important;
    border: none !important;
    border-bottom: 1px solid #f0f0f5 !important;
    border-radius: 0 !important;
    padding: 0.4rem 0.2rem !important;
    text-align: left !important;
    font-size: 0.85rem !important;
    color: #374151 !important;
    box-shadow: none !important;
    justify-content: flex-start !important;
}
div[data-testid="stVerticalBlock"] button[kind="secondary"]:hover {
    background: #f8f9ff !important;
    color: #4f46e5 !important;
}
</style>
"""
 
def _back(key="back"):
    if st.button("← Back", key=key):
        st.session_state.prof_vista = "lista"
        st.rerun()
 
 
# ─────────────────────────────────────────────────────────────────────────────
def vista_lista_estudiantes(db):
    st.markdown(STYLES, unsafe_allow_html=True)
 
    _, col_logout = st.columns([5, 1])
    with col_logout:
        if st.button("logout", key="logout_prof"):
            st.session_state.modo = None
            st.session_state.prof_vista = "lista"
            st.rerun()
 
    st.markdown("<div class='section-title'>Students</div>", unsafe_allow_html=True)
 
    estudiantes = list(db.collection("usuarios").where("rol", "==", "student").stream())
 
    if not estudiantes:
        st.caption("No students yet.")
    else:
        nombres = [e.to_dict()["id"] for e in estudiantes]
 
        # Search filter
        busqueda = st.text_input("", placeholder="🔍  Search student...", label_visibility="collapsed")
 
        if busqueda:
            filtrados = [n for n in nombres if busqueda.lower() in n.lower()]
            if not filtrados:
                st.caption("No match found.")
            else:
                for nombre in filtrados:
                    if st.button(f"  {nombre}", key=f"est_{nombre}", use_container_width=True):
                        st.session_state.estudiante_seleccionado = nombre
                        st.session_state.prof_vista = "detalle"
                        st.rerun()
        else:
            st.caption(f"{len(nombres)} students enrolled.")
 
    st.markdown("<div style='margin-top:1.2rem'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("＋ Add Student", use_container_width=True):
            st.session_state.prof_vista = "agregar"
            st.rerun()
    with c2:
        if st.button("📊 Stats", use_container_width=True):
            st.session_state.prof_vista = "estadisticas"
            st.rerun()
 
 
# ─────────────────────────────────────────────────────────────────────────────
def vista_agregar_estudiante(db):
    _back("back_agregar")
    st.markdown("<div class='section-title'>New Student</div>", unsafe_allow_html=True)
 
    with st.form("form_estudiante"):
        student_id = st.text_input("Student ID", placeholder="e.g. john_doe")
        if st.form_submit_button("Create", use_container_width=True, type="primary"):
            if not student_id.strip():
                st.error("Please enter a Student ID.")
            elif db.collection("usuarios").document(student_id).get().exists:
                st.error(f"'{student_id}' already exists.")
            else:
                db.collection("usuarios").document(student_id).set({
                    "id": student_id, "password": student_id, "rol": "student"
                })
                st.success(f"Student '{student_id}' created.")
                st.session_state.prof_vista = "lista"
                st.rerun()
 
 
# ─────────────────────────────────────────────────────────────────────────────
def vista_estadisticas(db, client):
    _back("back_stats")
    st.markdown("<div class='section-title'>Course Stats · Last 7 days</div>", unsafe_allow_html=True)
 
    hace_7 = (datetime.now() - timedelta(days=7)).isoformat()
    chats  = list(db.collection("chats").stream())
 
    activos, total_q, preguntas = [], 0, []
    for chat in chats:
        data = chat.to_dict()
        if data.get("ultima_actualizacion", "") >= hace_7:
            msgs = data.get("mensajes", [])
            qs   = [m for m in msgs if m.get("role") == "user"]
            activos.append(chat.id)
            total_q += len(qs)
            preguntas.extend(qs)
 
    c1, c2 = st.columns(2)
    c1.metric("Active Students", len(activos))
    c2.metric("Questions Asked", total_q)
 
    if activos:
        st.caption("Active: " + ", ".join(activos))
 
    st.divider()
 
    if st.button("🤖 Generate Weekly Report", use_container_width=True):
        if not preguntas:
            st.warning("No activity this week.")
        else:
            with st.spinner("Analyzing..."):
                texto  = "\n".join([f"- {m['content']}" for m in preguntas])
                prompt = f"""You are an assistant for a Calculus 1 professor.
Analyze these student questions from the past week:
 
{texto}
 
Generate a very short weekly instructor report in English.
Start directly with **Activity**. No title, no intro, no filler. Max 70 words.
 
## Weekly Summary
**Activity**
- Active students: X
- Questions: X
 
**Topics**
- Topic 1
 
**Doubts**
- Doubt 1
 
**Recommendation**
- Recommendation 1"""
                resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                st.markdown(resp.text)
 
 
# ─────────────────────────────────────────────────────────────────────────────
def vista_detalle_estudiante(db, student_id, client):
    _back("back_detalle")
    st.markdown(f"<div class='section-title'>{student_id}</div>", unsafe_allow_html=True)
 
    doc = db.collection("chats").document(student_id).get()
    if not doc.exists or not doc.to_dict().get("mensajes"):
        st.caption("No chat history yet.")
        return
 
    data      = doc.to_dict()
    mensajes  = data.get("mensajes", [])
    ultima    = data.get("ultima_actualizacion", "N/A")
    preguntas = [m for m in mensajes if m.get("role") == "user"]
 
    c1, c2, c3 = st.columns(3)
    c1.metric("Messages",  len(mensajes))
    c2.metric("Questions", len(preguntas))
    c3.metric("Last Active", ultima[:10] if ultima != "N/A" else "—")
 
    st.divider()
 
    tab1, tab2 = st.tabs(["💬 Chat", "🤖 Analysis"])
 
    with tab1:
        for msg in mensajes:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
 
    with tab2:
        if st.button("Generate Analysis", use_container_width=True):
            with st.spinner("Analyzing..."):
                historial = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in mensajes])
                prompt = f"""You are an assistant helping a Calculus I professor review a student's chat history.
Analyze the following student chat:
 
{historial}
 
Instructions:
- Always respond in English only.
- Be concise. Start directly with the analysis. No introduction.
 
Use exactly this structure:
 
1. Main topics consulted
- 2 to 4 bullet points
 
2. Recurrent doubts or confusions
- 2 to 4 bullet points
 
3. Topics with most difficulty
- 1 to 3 bullet points
 
4. Brief observation about learning pattern
- 2 to 4 bullet points
 
Keep it compact. Short bullets, no paragraphs."""
                resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                st.markdown(resp.text)