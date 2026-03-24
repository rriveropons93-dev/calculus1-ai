import streamlit as st
from datetime import datetime, timedelta

def vista_lista_estudiantes(db):
    st.subheader("Students")
    estudiantes = db.collection("usuarios").where("rol", "==", "student").stream()
    lista = list(estudiantes)

    if not lista:
        st.info("No students yet.")
    else:
        for est in lista:
            data = est.to_dict()
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(f"👤 {data['id']}", key=data['id']):
                    st.session_state.estudiante_seleccionado = data['id']
                    st.session_state.prof_vista = "detalle"
                    st.rerun()

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Add Student", use_container_width=True):
            st.session_state.prof_vista = "agregar"
            st.rerun()
    with col2:
        if st.button("📊 Course Stats", use_container_width=True):
            st.session_state.prof_vista = "estadisticas"
            st.rerun()


def vista_agregar_estudiante(db):
    st.subheader("➕ New Student")
    with st.form("form_estudiante"):
        student_id = st.text_input("Student ID")
        submitted = st.form_submit_button("Create Student")
        if submitted:
            if student_id.strip() == "":
                st.error("Please enter a Student ID.")
            else:
                doc = db.collection("usuarios").document(student_id).get()
                if doc.exists:
                    st.error(f"Student '{student_id}' already exists.")
                else:
                    db.collection("usuarios").document(student_id).set({
                        "id": student_id,
                        "password": student_id,
                        "rol": "student"
                    })
                    st.success(f"Student '{student_id}' created.")
                    st.session_state.prof_vista = "lista"
                    st.rerun()

    if st.button("Cancel"):
        st.session_state.prof_vista = "lista"
        st.rerun()


def vista_estadisticas(db, client):
    st.subheader("📊 Course Statistics")

    hace_7_dias = (datetime.now() - timedelta(days=7)).isoformat()
    chats = list(db.collection("chats").stream())

    estudiantes_activos = []
    total_preguntas = 0
    todas_las_preguntas = []

    for chat in chats:
        data = chat.to_dict()
        ultima = data.get("ultima_actualizacion", "")
        mensajes = data.get("mensajes", [])
        if ultima >= hace_7_dias:
            estudiantes_activos.append(chat.id)
            preguntas = [m for m in mensajes if m.get("role") == "user"]
            total_preguntas += len(preguntas)
            todas_las_preguntas.extend(preguntas)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Active Students This Week", len(estudiantes_activos))
    with col2:
        st.metric("Total Questions This Week", total_preguntas)

    if estudiantes_activos:
        st.markdown("**Active:** " + ", ".join(estudiantes_activos))

    st.markdown("---")

    if st.button("🤖 Generate Weekly Report", use_container_width=True):
        if not todas_las_preguntas:
            st.warning("No activity this week.")
        else:
            with st.spinner("Analyzing..."):
                texto = "\n".join([f"- {m['content']}" for m in todas_las_preguntas])
                prompt = f"""You are an assistant for a Calculus 1 professor.
Analyze these student questions from the past week:

{texto}

Generate a very short weekly instructor report in English.
No title or headerat the top. Start directly with **Activity**

Rules:
- No introduction.
- No filler.
- No unnecessary sections.
- Maximum 70 words.
- Use only these sections:

## Weekly Summary
**Activity**
- Active students: X
- Questions: X

**Topics**
- Topic 1
- Topic 2

**Doubts**
- Doubt 1
- Doubt 2

**Recommendation**
- Recommendation 1"""
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                st.markdown(response.text)

    if st.button("← Back"):
        st.session_state.prof_vista = "lista"
        st.rerun()


def vista_detalle_estudiante(db, student_id, client):
    st.subheader(f"👤 {student_id}")

    if st.button("← Back to Students"):
        st.session_state.prof_vista = "lista"
        st.rerun()

    doc = db.collection("chats").document(student_id).get()

    if not doc.exists or not doc.to_dict().get("mensajes"):
        st.info("This student has no chat history yet.")
        return

    data = doc.to_dict()
    mensajes = data.get("mensajes", [])
    ultima = data.get("ultima_actualizacion", "N/A")
    preguntas = [m for m in mensajes if m.get("role") == "user"]

    col1, col2, col3 = st.columns(3)
    col1.metric("Messages", len(mensajes))
    col2.metric("Questions", len(preguntas))
    col3.metric("Last Active", ultima[:10] if ultima != "N/A" else "N/A")

    st.markdown("---")

    tab1, tab2 = st.tabs(["💬 Full Chat", "🤖 AI Analysis"])

    with tab1:
        for msg in mensajes:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    with tab2:
        if st.button("Generate Analysis", use_container_width=True):
            with st.spinner("Analyzing with Gemini..."):
                historial = "\n".join(
                    [f"{m['role'].upper()}: {m['content']}" for m in mensajes])
                prompt = f"""You are an assistant helping a Calculus I professor review a student's chat history.
Analyze the following student chat:

{historial}

Instructions:
- Always respond in English only.
- Do not use Spanish at any point.
- Be concise, clear, and useful for the professor.
- Do not include any introduction, greeting, or preamble.
- Start directly with the analysis.
- Focus only on the student's learning patterns and academic needs.

Use exactly this structure:

1. Main topics consulted
- 2 to 4 short bullet points

2. Recurrent doubts or confusions
- 2 to 4 short bullet points

3. Topics where the student showed more difficulty
- 1 to 3 short bullet points

4. Brief observation about the student's learning pattern
- 2 to 4 short bullet points

Additional rules:
- Keep the full analysis compact.
- Use short bullet points, not long paragraphs.
- Do not repeat the same idea in multiple sections.
- If the data is limited, say so briefly in English.
- Do not mention the language of the original chat.
"""

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                st.markdown(response.text)