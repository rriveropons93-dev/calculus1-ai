import streamlit as st
from professor.professor_views import (
    vista_lista_estudiantes,
    vista_agregar_estudiante,
    vista_estadisticas,
    vista_detalle_estudiante
)

def modo_profesor(client,db):
    st.title("👨‍🏫 Professor Panel")
    st.markdown("---")

    if st.button("← Back"):
        st.session_state.modo = None
        st.session_state.prof_vista = "lista"
        st.rerun()

    if "prof_vista" not in st.session_state:
        st.session_state.prof_vista = "lista"

    if st.session_state.prof_vista == "lista":
        vista_lista_estudiantes(db)

    elif st.session_state.prof_vista == "agregar":
        vista_agregar_estudiante(db)

    elif st.session_state.prof_vista == "estadisticas":
        vista_estadisticas(db,client)

    elif st.session_state.prof_vista == "detalle":
        student_id = st.session_state.get("estudiante_seleccionado")
        vista_detalle_estudiante(db, student_id,client)