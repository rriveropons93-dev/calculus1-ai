import streamlit as st

def modo_profesor(db):
    st.title("👨‍🏫 Professor Panel")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("← Back"):
            st.session_state.modo = None
            st.rerun()
    
    st.subheader("Students")
    st.info("No students yet.")
    
    st.markdown("---")
    
    if st.button("➕ Add Student", use_container_width=True):
        st.session_state.agregar_estudiante = True
        st.rerun()
