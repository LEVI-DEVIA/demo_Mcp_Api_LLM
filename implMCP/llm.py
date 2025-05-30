import asyncio
import openai
from anthropic import Anthropic
from mcp_client import MCPClient
import os


class MCPLLMService:
    def __init__(self):
        # Tu devras mettre tes vraies clés API ici
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.claude_client = Anthropic(api_key="")
        self.mcp_client = None
        self._connection_lock = asyncio.Lock()

    async def __aenter__(self):
        """Context manager entry"""
        await self.init_mcp()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.close_mcp()

    async def init_mcp(self):
        """Initialise la connexion MCP de manière thread-safe"""
        async with self._connection_lock:
            if self.mcp_client and self.mcp_client.connected:
                print("MCP déjà connecté")
                return True

            print("Initialisation de la connexion MCP...")
            self.mcp_client = MCPClient()
            print("Connexion au serveur MCP...")
            success = await self.mcp_client.connect()
            if success:
                print("MCP connecté avec succès")
            else:
                print("Échec de connexion MCP")
            return success

    async def close_mcp(self):
        """Ferme la connexion MCP"""
        if self.mcp_client:
            await self.mcp_client.disconnect()
            self.mcp_client = None

    async def ensure_mcp_connection(self):
        """S'assure que MCP est connecté avant utilisation"""
        if not self.mcp_client or not self.mcp_client.connected:
            await self.init_mcp()
        return self.mcp_client and self.mcp_client.connected

    async def process_with_openai(self, user_query):
        """Traite la requête avec OpenAI en utilisant MCP"""
        print(f"Use function process_with_openai")

        # S'assurer que MCP est connecté
        if not await self.ensure_mcp_connection():
            return "Erreur: Impossible de se connecter au serveur MCP"

        try:
            mcp_data = await self._get_mcp_data(user_query)
        except Exception as e:
            return f"Erreur lors de la récupération des données MCP: {str(e)}"

        prompt = f"""
        L'utilisateur demande: {user_query}
        
        Données récupérées via MCP: {mcp_data}
        
        Réponds de manière naturelle en utilisant ces données.
        Si il y a une erreur dans les données, explique-le gentiment.
        """

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.2,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Erreur OpenAI: {str(e)}"

    async def process_with_claude(self, user_query):
        """Traite la requête avec Claude en utilisant MCP"""
        # S'assurer que MCP est connecté
        if not await self.ensure_mcp_connection():
            return "Erreur: Impossible de se connecter au serveur MCP"

        try:
            mcp_data = await self._get_mcp_data(user_query)
        except Exception as e:
            return f"Erreur lors de la récupération des données MCP: {str(e)}"

        prompt = f"""
        L'utilisateur demande: {user_query}
        
        Données récupérées via MCP: {mcp_data}
        
        Réponds de manière naturelle en utilisant ces données.
        Si il y a une erreur dans les données, explique-le gentiment.
        """

        try:
            response = self.claude_client.messages.create(
                model="claude-3-haiku-20240307",  # Modèle valide
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        except Exception as e:
            return f"Erreur Claude: {str(e)}"

    async def _get_mcp_data(self, query):
        """Récupère les données via MCP selon le type de requête"""
        if not self.mcp_client or not self.mcp_client.connected:
            return {"error": "MCP non connecté"}

        query_lower = query.lower()

        try:
            if any(
                word in query_lower
                for word in ["ingrédient", "plat", "nourriture", "recette"]
            ):
                # Question sur la nourriture
                food_name = self._extract_food_name(query)
                return await self.mcp_client.get_food_ingredients(food_name)

            elif any(
                word in query_lower for word in ["livre", "auteur", "roman", "histoire"]
            ):
                # Question sur les livres
                book_name = self._extract_book_name(query)
                return await self.mcp_client.get_book_info(book_name)

            elif "liste" in query_lower and "plat" in query_lower:
                return await self.mcp_client.list_foods()

            elif "liste" in query_lower and "livre" in query_lower:
                return await self.mcp_client.list_books()

            else:
                return {"info": "Pas de données spécifiques récupérées via MCP"}
        except Exception as e:
            return {"error": f"Erreur lors de l'accès aux données: {str(e)}"}

    def _extract_food_name(self, query):
        """Extrait le nom du plat de la requête"""
        foods = ["pizza", "salade", "omelette", "pâtes"]
        for food in foods:
            if food in query.lower():
                return food
        return "pizza"  # Par défaut

    def _extract_book_name(self, query):
        """Extrait le nom du livre de la requête"""
        books = ["1984", "gatsby", "hamlet"]
        for book in books:
            if book in query.lower():
                return book
        return "1984"  # Par défaut
