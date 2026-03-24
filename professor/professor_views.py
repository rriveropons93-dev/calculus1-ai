import streamlit as st
from datetime import datetime, timedelta

STYLES = """
<style>
.section-title {
    font-size: 0.7rem; font-weight: 600; letter-spacing: 0.08em;
    text-transform: uppercase; color: #9ca3af; margin-bottom: 0.4rem;
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
            st.query_params.clear()
            st.rerun()

    st.markdown("<div class='section-title'>Students</div>", unsafe_allow_html=True)

    estudiantes = list(db.collection("usuarios").where("rol", "==", "student").stream())

    if not estudiantes:
        st.caption("No students yet.")
    else:
        nombres = [e.to_dict()["id"] for e in estudiantes]
        busqueda = st.text_input("", placeholder="🔍  Search student...", label_visibility="collapsed")
        filtrados = [n for n in nombres if busqueda.lower() in n.lower()] if busqueda else nombres

        rows_html = "".join([
            f'<a href="?modo=professor&open_student={n}" target="_self" style="'
            'display:block;padding:6px 10px;font-size:0.82rem;color:#374151;'
            'text-decoration:none;border-bottom:1px solid #f0f0f5;"'
            f'onmouseover="this.style.background=\'#f3f4ff\';this.style.color=\'#4f46e5\'"'
            f'onmouseout="this.style.background=\'\';this.style.color=\'#374151\'">{n}</a>'
            for n in filtrados
        ])

        with st.expander(f"All students ({len(filtrados)})"):
            st.markdown(
                f'<div style="margin:-8px -16px;overflow:hidden;">{rows_html}</div>',
                unsafe_allow_html=True
            )

    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
    if st.button("📊 Course Stats", use_container_width=True):
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
                texto = "\n".join([f"- {m['content']}" for m in preguntas])
                prompt = f"""You are an assistant for a Calculus 1 professor.
Analyze these student questions from the past week:\n{texto}\n
Generate a very short weekly instructor report in English.
Start directly with **Activity**. No title, no intro. Max 70 words.
## Weekly Summary
**Activity**\n- Active students: X\n- Questions: X
**Topics**\n- Topic 1
**Doubts**\n- Doubt 1
**Recommendation**\n- Recommendation 1"""
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
Analyze:\n{historial}\n
- English only. Start directly. No intro.
1. Main topics consulted (2-4 bullets)
2. Recurrent doubts (2-4 bullets)
3. Most difficult topics (1-3 bullets)
4. Learning pattern observation (2-4 bullets)
Short bullets only."""
                resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                st.markdown(resp.text)