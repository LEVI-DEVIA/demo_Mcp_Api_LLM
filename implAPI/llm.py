import requests
import openai
from anthropic import Anthropic
import os


class LLMService:
    def __init__(self):
        # Tu devras mettre tes vraies clés API ici
        self.openai_client = openai.OpenAI(
            api_key="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"
        )
        self.claude_client = Anthropic(api_key="")
        self.api_base_url = "http://localhost:8000"

    def call_food_api(self, food_name):
        """Appelle l'API nourriture"""
        try:
            response = requests.get(f"{self.api_base_url}/food/{food_name}")
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": "Plat non trouvé"}
        except Exception as e:
            return {"error": f"Erreur API: {str(e)}"}

    def call_book_api(self, book_name):
        """Appelle l'API livre"""
        try:
            response = requests.get(f"{self.api_base_url}/book/{book_name}")
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": "Livre non trouvé"}
        except Exception as e:
            return {"error": f"Erreur API: {str(e)}"}

    def process_with_openai(self, user_query):
        """Traite la requête avec OpenAI"""
        # Détermine si c'est une question sur la nourriture ou les livres
        if any(
            word in user_query.lower()
            for word in ["ingrédient", "plat", "nourriture", "recette"]
        ):
            # Extrait le nom du plat (logique simple)
            food_name = self._extract_food_name(user_query)
            api_result = self.call_food_api(food_name)

            prompt = f"""
            L'utilisateur demande: {user_query}
            
            Données de l'API: {api_result}
            
            Réponds de manière naturelle en utilisant ces données.
            """
        elif any(
            word in user_query.lower()
            for word in ["livre", "auteur", "roman", "histoire"]
        ):
            book_name = self._extract_book_name(user_query)
            api_result = self.call_book_api(book_name)

            prompt = f"""
            L'utilisateur demande: {user_query}
            
            Données de l'API: {api_result}
            
            Réponds de manière naturelle en utilisant ces données.
            """
        else:
            prompt = f"Réponds à cette question: {user_query}"

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

    def process_with_claude(self, user_query):
        """Traite la requête avec Claude"""
        if any(
            word in user_query.lower()
            for word in ["ingrédient", "plat", "nourriture", "recette"]
        ):
            food_name = self._extract_food_name(user_query)
            api_result = self.call_food_api(food_name)

            prompt = f"""
            L'utilisateur demande: {user_query}
            
            Données de l'API: {api_result}
            
            Réponds de manière naturelle en utilisant ces données.
            """
        elif any(
            word in user_query.lower()
            for word in ["livre", "auteur", "roman", "histoire"]
        ):
            book_name = self._extract_book_name(user_query)
            api_result = self.call_book_api(book_name)

            prompt = f"""
            L'utilisateur demande: {user_query}
            
            Données de l'API: {api_result}
            
            Réponds de manière naturelle en utilisant ces données.
            """
        else:
            prompt = f"Réponds à cette question: {user_query}"

        try:
            response = self.claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        except Exception as e:
            return f"Erreur Claude: {str(e)}"

    def _extract_food_name(self, query):
        """Extrait le nom du plat de la requête (logique simple)"""
        foods = ["pizza", "salade", "omelette", "pâtes"]
        for food in foods:
            if food in query.lower():
                return food
        return "pizza"  # Par défaut

    def _extract_book_name(self, query):
        """Extrait le nom du livre de la requête (logique simple)"""
        books = ["1984", "gatsby", "hamlet"]
        for book in books:
            if book in query.lower():
                return book
        return "1984"  # Par défaut
