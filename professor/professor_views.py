import streamlit as st
from google.cloud.firestore_v1.base_query import FieldFilter
from datetime import datetime, timedelta

def vista_lista_estudiantes(db):
    st.subheader("Students")
    estudiantes = db.collection("usuarios").where(
        filter=FieldFilter("rol", "==", "student")).stream()
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
                prompt = f"""Eres un asistente para un profesor de Cálculo 1.
Analiza estas preguntas de estudiantes de la última semana:

{texto}

Responde en español con:
1. Top 3-5 temas más consultados
2. Dudas recurrentes principales
3. Temas que recomiendas reforzar en clase

Sé conciso y directo."""
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
                prompt = f"""Eres un asistente para un profesor de Cálculo 1.
Analiza el siguiente historial de chat de un estudiante:

{historial}

Respond in English with :
1. Temas principales consultados
2. Dudas recurrentes o confusiones
3. Temas donde tuvo más dificultad
4. Observación breve sobre el patrón de aprendizaje del estudiante

Sé conciso y útil para el profesor.
Do not include any introduction or preamble.
Start directly with the analysis."""
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                st.markdown(response.text)