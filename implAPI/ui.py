import streamlit as st
from llm import LLMService

# Configuration de la page
st.set_page_config(page_title="Demo API vs MCP", page_icon="🤖", layout="wide")

st.title("Demo: LLM avec APIs")


# Initialise le service LLM
@st.cache_resource
def init_llm_service():
    return LLMService()


llm_service = init_llm_service()

# Interface utilisateur
col1, col2 = st.columns(2)

with col1:
    st.subheader("Données disponibles")
    st.write("**Plats:** pizza, salade, omelette, pâtes")
    st.write("**Livres:** 1984, gatsby, hamlet")

with col2:
    st.subheader("Exemples de questions")
    st.write("- Quels sont les ingrédients de la pizza ?")
    st.write("- Parle-moi du livre 1984")
    st.write("- Comment faire une omelette ?")

# Zone de saisie
user_query = st.text_input(
    "Pose ta question:", placeholder="Ex: Quels ingrédients pour la pizza ?"
)

# Boutons pour choisir le modèle
col1, col2 = st.columns(2)

with col1:
    if st.button("🟢 OpenAI", use_container_width=True):
        if user_query:
            with st.spinner("OpenAI réfléchit..."):
                response = llm_service.process_with_openai(user_query)
                st.success("Réponse OpenAI:")
                st.write(response)
        else:
            st.warning("Tape une question d'abord!")

with col2:
    if st.button("🔵 Claude", use_container_width=True):
        if user_query:
            with st.spinner("Claude réfléchit..."):
                response = llm_service.process_with_claude(user_query)
                st.success("Réponse Claude:")
                st.write(response)
        else:
            st.warning("Tape une question d'abord!")
