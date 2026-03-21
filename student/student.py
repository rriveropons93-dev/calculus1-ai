import streamlit as st
from utils.pdf_utils import cargar_pdfs
from utils.prompt import get_prompt

def modo_student(client, db):
    st.title("📚 Calculus 1 AI Assistant")
    st.markdown("<small>Developed by Roger Riveropons | rriveropons93@gmail.com</small>", unsafe_allow_html=True)

    if "student_id" not in st.session_state:
        st.session_state.student_id = None

    if st.session_state.student_id is None:
        st.subheader("Student Login")
        with st.form("login_form"):
            student_id = st.text_input("Student ID")
            submitted = st.form_submit_button("Login")
            if submitted:
                if student_id.strip() == "":
                    st.error("Please enter your Student ID.")
                else:
                    doc = db.collection("usuarios").document(student_id).get()
                    if doc.exists and doc.to_dict().get("rol") == "student":
                        st.session_state.student_id = student_id
                        doc = db.collection("chats").document(student_id).get()
                        if doc.exists:
                            st.session_state.mensajes = doc.to_dict().get("mensajes",[])
                        else:
                            st.session_state.mensajes = []
                        st.rerun()
                    else:
                        st.error("Student ID not found.")
        if st.button("← Back"):
            st.session_state.modo = None
            st.rerun()
        return

    student_id = st.session_state.student_id
    material = cargar_pdfs()

    if st.button("← Back"):
        st.session_state.modo = None
        st.session_state.student_id = None
        st.session_state.mensajes = []
        st.rerun()

    st.success(f"Welcome, {student_id}!")

    if "mensajes" not in st.session_state:
        doc = db.collection("chats").document(student_id).get()
        if doc.exists:
            st.session_state.mensajes = doc.to_dict().get("mensajes", [])
        else:
            st.session_state.mensajes = []

    for msg in st.session_state.mensajes:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if pregunta := st.chat_input("What do you want to study?"):
        st.session_state.mensajes.append({"role": "user", "content": pregunta})
        with st.chat_message("user"):
            st.write(pregunta)

        prompt = get_prompt(material, pregunta)

        st.markdown('<div id="top-response"></div>', unsafe_allow_html=True)
        st.markdown("<br><br>", unsafe_allow_html=True)

        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                st.write(response.text)

        st.session_state.mensajes.append({"role": "assistant", "content": response.text})

        # Guardar en Firebase
        db.collection("chats").document(student_id).set({
            "mensajes": st.session_state.mensajes
        })

        st.components.v1.html("""
        <script>
            setTimeout(function() {
                window.parent.document.getElementById('top-response').scrollIntoView({behavior: 'smooth', block: 'start'});
            }, 1200);
        </script>
        """, height=0)