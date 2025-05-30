import asyncio
import json
import subprocess
from contextlib import AsyncExitStack
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


class MCPClient:
    def __init__(self):
        self.session = None
        self.connected = False
        self.exit_stack = None
        self.stdio_transport = None

    async def connect(self):
        """Se connecte au serveur MCP"""
        try:
            # Créer l'exit stack ici pour éviter les problèmes de contexte
            self.exit_stack = AsyncExitStack()

            # Configuration du serveur MCP FastMCP
            server_params = StdioServerParameters(
                command="python", args=["mcp_server.py"]
            )

            # Utilisation de stdio_client avec AsyncExitStack
            self.stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )

            # Récupération des streams
            read_stream, write_stream = self.stdio_transport

            # Création de la session avec les streams
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )

            # Initialisation de la session
            init_result = await self.session.initialize()

            self.connected = True
            print("Connecté au serveur MCP")
            print(f"Serveur info: {init_result}")

            # Optionnel: Lister les outils disponibles
            try:
                tools_response = await self.session.list_tools()
                print(
                    f"Outils disponibles: {[tool.name for tool in tools_response.tools]}"
                )
            except Exception as e:
                print(f"Impossible de lister les outils: {e}")

            return True

        except Exception as e:
            print(f"Erreur de connexion: {e}")
            print(f"Type d'erreur: {type(e)}")
            import traceback

            traceback.print_exc()

            # Nettoyer en cas d'erreur
            await self._cleanup()
            return False

    async def _cleanup(self):
        """Nettoie les ressources de manière sûre"""
        try:
            if self.exit_stack:
                await self.exit_stack.aclose()
                self.exit_stack = None
        except Exception as e:
            print(f"Erreur lors du nettoyage: {e}")
        finally:
            self.connected = False
            self.session = None
            self.stdio_transport = None

    async def disconnect(self):
        """Se déconnecte du serveur MCP"""
        try:
            if self.connected:
                print("Déconnexion du serveur MCP...")
                await self._cleanup()
                print("Déconnecté du serveur MCP")
        except Exception as e:
            print(f"Erreur lors de la déconnexion: {e}")

    async def get_food_ingredients(self, food_name):
        """Récupère les ingrédients d'un plat"""
        if not self.connected:
            return {"error": "Pas connecté au serveur MCP"}

        try:
            result = await self.session.call_tool(
                "get_food_ingredients", {"food_name": food_name}
            )

            # Gestion du résultat selon le type de contenu
            if result.content:
                if hasattr(result.content[0], "text"):
                    return json.loads(result.content[0].text)
                else:
                    return {"data": str(result.content[0])}
            else:
                return {"error": "Aucun contenu dans la réponse"}

        except json.JSONDecodeError as e:
            return {"error": f"Erreur de parsing JSON: {str(e)}"}
        except Exception as e:
            return {"error": f"Erreur MCP: {str(e)}"}

    async def get_book_info(self, book_name):
        """Récupère les infos d'un livre"""
        if not self.connected:
            return {"error": "Pas connecté au serveur MCP"}

        try:
            result = await self.session.call_tool(
                "get_book_info", {"book_name": book_name}
            )

            # Gestion du résultat selon le type de contenu
            if result.content:
                if hasattr(result.content[0], "text"):
                    return json.loads(result.content[0].text)
                else:
                    return {"data": str(result.content[0])}
            else:
                return {"error": "Aucun contenu dans la réponse"}

        except json.JSONDecodeError as e:
            return {"error": f"Erreur de parsing JSON: {str(e)}"}
        except Exception as e:
            return {"error": f"Erreur MCP: {str(e)}"}

    async def list_foods(self):
        """Liste tous les plats"""
        if not self.connected:
            return {"error": "Pas connecté au serveur MCP"}

        try:
            result = await self.session.call_tool("list_available_foods", {})

            # Gestion du résultat selon le type de contenu
            if result.content:
                if hasattr(result.content[0], "text"):
                    return json.loads(result.content[0].text)
                else:
                    return {"data": str(result.content[0])}
            else:
                return {"error": "Aucun contenu dans la réponse"}

        except json.JSONDecodeError as e:
            return {"error": f"Erreur de parsing JSON: {str(e)}"}
        except Exception as e:
            return {"error": f"Erreur MCP: {str(e)}"}

    async def list_books(self):
        """Liste tous les livres"""
        if not self.connected:
            return {"error": "Pas connecté au serveur MCP"}

        try:
            result = await self.session.call_tool("list_available_books", {})

            # Gestion du résultat selon le type de contenu
            if result.content:
                if hasattr(result.content[0], "text"):
                    return json.loads(result.content[0].text)
                else:
                    return {"data": str(result.content[0])}
            else:
                return {"error": "Aucun contenu dans la réponse"}

        except json.JSONDecodeError as e:
            return {"error": f"Erreur de parsing JSON: {str(e)}"}
        except Exception as e:
            return {"error": f"Erreur MCP: {str(e)}"}

    # Méthode pour utiliser le client avec un context manager
    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()


# Fonction principale corrigée
async def main():
    """Fonction principale pour tester le client"""
    client = MCPClient()

    try:
        # Test de connexion
        if await client.connect():
            print("\n=== Test de fonctionnalités ===")

            # Test liste des aliments
            foods = await client.list_foods()
            print(f"Liste des aliments: {foods}")

            # Test liste des livres
            books = await client.list_books()
            print(f"Liste des livres: {books}")

            # Attendre un peu pour laisser les opérations se terminer
            await asyncio.sleep(0.1)

    except Exception as e:
        print(f"Erreur dans main: {e}")
    finally:
        # Déconnexion propre
        await client.disconnect()
        # Attendre que toutes les tâches se terminent proprement
        await asyncio.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(main())
