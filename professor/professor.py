import streamlit as st
from professor.professor_views import (
    vista_lista_estudiantes,
    vista_agregar_estudiante,
    vista_estadisticas,
    vista_detalle_estudiante
)
 
def modo_profesor(client, db):
    st.session_state.setdefault("prof_vista", "lista")
 
    st.markdown("""
    <style>
    .block-container { max-width: 560px; padding-top: 2rem; }
    .prof-header {
        display: flex; align-items: center; gap: 10px;
        margin-bottom: 0.2rem;
    }
    .prof-header h2 {
        font-size: 1.15rem; font-weight: 600;
        color: #1a1a2e; margin: 0;
    }
    .prof-sub {
        font-size: 0.75rem; color: #9ca3af;
        margin-bottom: 1.2rem;
    }
    </style>
    """, unsafe_allow_html=True)
 
    st.markdown("<div class='prof-header'><span>👨‍🏫</span><h2>Professor Panel</h2></div>", unsafe_allow_html=True)
    st.markdown("<div class='prof-sub'>Brennan · Calculus 1</div>", unsafe_allow_html=True)
 
    if st.session_state.prof_vista == "lista":
        vista_lista_estudiantes(db)
    elif st.session_state.prof_vista == "agregar":
        vista_agregar_estudiante(db)
    elif st.session_state.prof_vista == "estadisticas":
        vista_estadisticas(db, client)
    elif st.session_state.prof_vista == "detalle":
        vista_detalle_estudiante(db, st.session_state.get("estudiante_seleccionado"), client)