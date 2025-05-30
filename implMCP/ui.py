import streamlit as st
import asyncio
from llm import MCPLLMService


st.set_page_config(page_title="Demo MCP vs API", page_icon="🔗", layout="wide")

st.title("Demo: LLM avec MCP")


# Initialisation du serveur MCP - Sans cache pour éviter les problèmes de contexte
def get_mcp_service():
    """Crée une nouvelle instance du service à chaque fois"""
    return MCPLLMService()


# Fonction pour gérer les appels async avec gestion d'erreur améliorée
async def process_query_with_openai(query):
    service = get_mcp_service()
    try:
        return await service.process_with_openai(query)
    except Exception as e:
        return f"Erreur lors du traitement: {str(e)}"
    finally:
        # Nettoyage explicite
        try:
            await service.close_mcp()
        except Exception as cleanup_error:
            print(f"Erreur lors du nettoyage: {cleanup_error}")


async def process_query_with_claude(query):
    service = get_mcp_service()
    try:
        return await service.process_with_claude(query)
    except Exception as e:
        return f"Erreur lors du traitement: {str(e)}"
    finally:
        # Nettoyage explicite
        try:
            await service.close_mcp()
        except Exception as cleanup_error:
            print(f"Erreur lors du nettoyage: {cleanup_error}")


async def test_mcp_connection():
    """Test de connexion MCP avec nettoyage approprié"""
    service = get_mcp_service()
    try:
        success = await service.init_mcp()
        return success
    except Exception as e:
        print(f"Erreur lors du test de connexion: {e}")
        return False
    finally:
        try:
            await service.close_mcp()
        except Exception as cleanup_error:
            print(f"Erreur lors du nettoyage: {cleanup_error}")


# Interface utilisateur
col1, col2 = st.columns(2)

with col1:
    st.subheader("Données disponibles (via MCP)")
    st.write("**Plats:** pizza, salade, omelette, pâtes")
    st.write("**Livres:** 1984, gatsby, hamlet")

with col2:
    st.subheader("Exemples de questions")
    st.write("- Quels sont les ingrédients de la pizza ?")
    st.write("- Parle-moi du livre 1984")

# Saisie
user_query = st.text_input(
    "Pose ta question:", placeholder="Ex: Quels ingrédients pour la pizza ?"
)

# Boutons
col1, col2 = st.columns(2)

with col1:
    if st.button("🟢 OpenAI (MCP)", use_container_width=True):
        print("Bouton OpenAI cliqué")
        if user_query:
            with st.spinner("OpenAI + MCP travaillent..."):
                try:
                    # Utilisation d'asyncio.create_task pour une meilleure gestion
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        response = loop.run_until_complete(
                            process_query_with_openai(user_query)
                        )
                        st.success("Réponse OpenAI (via MCP):")
                        st.write(response)
                    finally:
                        # Nettoyage explicite de la boucle
                        pending = asyncio.all_tasks(loop)
                        for task in pending:
                            task.cancel()
                        loop.close()
                except Exception as e:
                    st.error(f"Erreur: {e}")
                    print(f"Erreur détaillée: {e}")
        else:
            st.warning("Tape une question d'abord!")

with col2:
    if st.button("🔵 Claude (MCP)", use_container_width=True):
        if user_query:
            with st.spinner("Claude + MCP travaillent..."):
                try:
                    # Même approche pour Claude
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        response = loop.run_until_complete(
                            process_query_with_claude(user_query)
                        )
                        st.success("Réponse Claude (via MCP):")
                        st.write(response)
                    finally:
                        pending = asyncio.all_tasks(loop)
                        for task in pending:
                            task.cancel()
                        loop.close()
                except Exception as e:
                    st.error(f"Erreur: {e}")
                    print(f"Erreur détaillée: {e}")
        else:
            st.warning("Tape une question d'abord!")

# Statut de connexion MCP
if st.button("Tester connexion MCP"):
    print("Test de connexion MCP...")
    with st.spinner("Test de connexion..."):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                success = loop.run_until_complete(test_mcp_connection())
                if success:
                    st.success("Connexion MCP OK!")
                else:
                    st.error("Échec de connexion MCP")
            finally:
                pending = asyncio.all_tasks(loop)
                for task in pending:
                    task.cancel()
                loop.close()
        except Exception as e:
            st.error(f"Erreur: {e}")
            print(f"Erreur détaillée: {e}")
