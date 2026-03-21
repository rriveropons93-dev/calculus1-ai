import streamlit as st
from google.cloud.firestore_v1.base_query import FieldFilter

def vista_lista_estudiantes(db):
    st.subheader("Students")
    estudiantes = db.collection("usuarios").where(filter = FieldFilter("rol", "==", "student")).stream()
    lista = list(estudiantes)

    if not lista:
        st.info("No students yet.")
    else:
        for est in lista:
            data = est.to_dict()
            if st.button(f"👤 {data['id']}", key=data['id']):
                st.session_state.estudiante_seleccionado = data['id']
                st.session_state.prof_vista = "detalle"
                st.rerun()

    st.markdown("---")
    if st.button("➕ Add Student", use_container_width=True):
        st.session_state.prof_vista = "agregar"
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


def vista_estadisticas(db):
    st.subheader("📊 Course Statistics")
    st.info("Coming soon.")


def vista_detalle_estudiante(db, student_id):
    st.subheader(f"👤 {student_id}")
    st.info("Chat history coming soon.")
    if st.button("← Back to Students"):
        st.session_state.prof_vista = "lista"
        st.rerun()